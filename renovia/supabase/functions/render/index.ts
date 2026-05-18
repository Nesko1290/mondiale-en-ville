// Renovia — Edge Function "render"
// Prend un projectId, recupere la photo source dans Storage, appelle Replicate
// (ControlNet/SDXL img2img) avec un prompt derive du style, telecharge le
// rendu, le repose dans Storage sous {user_id}/renders/, met a jour la
// colonne projects.rendered_path et renvoie le path + une signed URL.
//
// Deno runtime (Supabase Edge Functions).
// Deploy : supabase functions deploy render --no-verify-jwt=false
// Secrets : supabase secrets set REPLICATE_API_TOKEN=r8_... \
//                                REPLICATE_MODEL=stability-ai/sdxl:39ed...

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

type Body = { projectId: string; style?: string };

const STYLE_PROMPT: Record<string, string> = {
  moderne:
    "modern interior, clean lines, warm beige walls, designer furniture, soft natural light, photorealistic",
  minimaliste:
    "minimalist interior, white walls, light oak floor, scandinavian style, photorealistic",
  classique:
    "classic interior, elegant wainscoting, soft cream walls, vintage decor, warm lighting, photorealistic",
  scandinave:
    "scandinavian interior, light wood, soft pastels, cozy textiles, natural daylight, photorealistic",
};

Deno.serve(async (req) => {
  if (req.method !== "POST") {
    return json({ error: "Method not allowed" }, 405);
  }

  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return json({ error: "Missing auth" }, 401);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const replicateToken = Deno.env.get("REPLICATE_API_TOKEN");
  const replicateModel =
    Deno.env.get("REPLICATE_MODEL") ??
    "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b";

  if (!replicateToken) return json({ error: "REPLICATE_API_TOKEN not set" }, 500);

  // Client lie a l'utilisateur (pour lire la session)
  const userClient = createClient(supabaseUrl, Deno.env.get("SUPABASE_ANON_KEY")!, {
    global: { headers: { Authorization: authHeader } },
  });
  const { data: userRes, error: userErr } = await userClient.auth.getUser();
  if (userErr || !userRes.user) return json({ error: "Unauthenticated" }, 401);
  const userId = userRes.user.id;

  // Client service-role pour les ecritures
  const admin = createClient(supabaseUrl, serviceKey);

  let body: Body;
  try {
    body = (await req.json()) as Body;
  } catch {
    return json({ error: "Invalid JSON body" }, 400);
  }
  if (!body.projectId) return json({ error: "projectId required" }, 400);

  const { data: project, error: projErr } = await admin
    .from("projects")
    .select("id, user_id, photo_path, style")
    .eq("id", body.projectId)
    .maybeSingle();
  if (projErr || !project) return json({ error: "Project not found" }, 404);
  if (project.user_id !== userId) return json({ error: "Forbidden" }, 403);
  if (!project.photo_path) return json({ error: "Project has no photo" }, 400);

  const style = (body.style ?? project.style ?? "moderne") as string;
  const prompt = STYLE_PROMPT[style] ?? STYLE_PROMPT.moderne;

  // 1. Signed URL temporaire de la photo source
  const { data: signed, error: signedErr } = await admin.storage
    .from("project-photos")
    .createSignedUrl(project.photo_path, 600);
  if (signedErr || !signed) return json({ error: "Cannot sign source photo" }, 500);

  // 2. Lancer la prediction Replicate
  const startRes = await fetch("https://api.replicate.com/v1/predictions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Token ${replicateToken}`,
      Prefer: "wait=30",
    },
    body: JSON.stringify({
      version: replicateModel.split(":")[1] ?? replicateModel,
      input: {
        image: signed.signedUrl,
        prompt,
        strength: 0.55,
        guidance_scale: 7,
        num_inference_steps: 30,
      },
    }),
  });
  const prediction = await startRes.json();
  if (!startRes.ok) return json({ error: "Replicate start failed", detail: prediction }, 502);

  // 3. Poll jusqu'a completion (Prefer: wait=30 a deja patiente ; on poll si toujours en cours)
  const finished = await waitForPrediction(prediction, replicateToken);
  if (finished.status !== "succeeded") {
    return json({ error: `Prediction ${finished.status}`, detail: finished.error }, 502);
  }
  const outputs = Array.isArray(finished.output) ? finished.output : [finished.output];
  const renderedUrl = outputs[outputs.length - 1] as string | undefined;
  if (!renderedUrl) return json({ error: "No output from model" }, 502);

  // 4. Telecharger le rendu et le re-uploader dans le bucket prive
  const imgRes = await fetch(renderedUrl);
  if (!imgRes.ok) return json({ error: "Cannot fetch rendered image" }, 502);
  const bytes = new Uint8Array(await imgRes.arrayBuffer());

  const renderedPath = `${userId}/renders/${project.id}-${Date.now()}.png`;
  const { error: uploadErr } = await admin.storage
    .from("project-photos")
    .upload(renderedPath, bytes, { contentType: "image/png", upsert: false });
  if (uploadErr) return json({ error: "Upload failed", detail: uploadErr.message }, 500);

  // 5. Persister rendered_path sur projects
  await admin
    .from("projects")
    .update({ rendered_path: renderedPath, updated_at: new Date().toISOString() })
    .eq("id", project.id);

  // 6. Renvoyer un signed URL pour affichage immediat
  const { data: outSigned } = await admin.storage
    .from("project-photos")
    .createSignedUrl(renderedPath, 3600);

  return json({
    renderedPath,
    renderedUrl: outSigned?.signedUrl ?? null,
  });
});

async function waitForPrediction(initial: any, token: string): Promise<any> {
  let p = initial;
  const start = Date.now();
  while (p.status !== "succeeded" && p.status !== "failed" && p.status !== "canceled") {
    if (Date.now() - start > 60_000) return { ...p, status: "failed", error: "timeout" };
    await new Promise((r) => setTimeout(r, 2000));
    const r = await fetch(p.urls?.get ?? `https://api.replicate.com/v1/predictions/${p.id}`, {
      headers: { Authorization: `Token ${token}` },
    });
    p = await r.json();
  }
  return p;
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

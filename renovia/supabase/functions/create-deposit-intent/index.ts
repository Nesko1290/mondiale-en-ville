// Renovia — Edge Function "create-deposit-intent"
// Cree un PaymentIntent Stripe pour l'acompte d'une reservation.
// Retourne le client_secret + ephemeralKey + customer (pour PaymentSheet RN).
//
// Deno runtime.
// Secrets : supabase secrets set STRIPE_SECRET_KEY=sk_test_...
// Deploy  : supabase functions deploy create-deposit-intent

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

type Body = { bookingId: string };

Deno.serve(async (req) => {
  if (req.method !== "POST") return json({ error: "Method not allowed" }, 405);

  const authHeader = req.headers.get("Authorization");
  if (!authHeader) return json({ error: "Missing auth" }, 401);

  const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
  if (!stripeKey) return json({ error: "STRIPE_SECRET_KEY not set" }, 500);

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const anonKey = Deno.env.get("SUPABASE_ANON_KEY")!;

  const userClient = createClient(supabaseUrl, anonKey, {
    global: { headers: { Authorization: authHeader } },
  });
  const { data: userRes, error: userErr } = await userClient.auth.getUser();
  if (userErr || !userRes.user) return json({ error: "Unauthenticated" }, 401);
  const userId = userRes.user.id;

  const admin = createClient(supabaseUrl, serviceKey);

  let body: Body;
  try {
    body = (await req.json()) as Body;
  } catch {
    return json({ error: "Invalid JSON body" }, 400);
  }
  if (!body.bookingId) return json({ error: "bookingId required" }, 400);

  const { data: booking, error: bookErr } = await admin
    .from("bookings")
    .select("id, user_id, deposit_chf, deposit_paid")
    .eq("id", body.bookingId)
    .maybeSingle();
  if (bookErr || !booking) return json({ error: "Booking not found" }, 404);
  if (booking.user_id !== userId) return json({ error: "Forbidden" }, 403);
  if (booking.deposit_paid) return json({ error: "Already paid" }, 409);
  if (!booking.deposit_chf || booking.deposit_chf <= 0) {
    return json({ error: "No deposit amount" }, 400);
  }

  const amountCents = Math.round(Number(booking.deposit_chf) * 100);

  // Customer Stripe : on en cree un par appel (simple ; en prod, le persister sur profiles.stripe_customer_id)
  const customer = await stripe(stripeKey, "POST", "customers", {
    metadata: { user_id: userId },
  });
  if (!customer.id) return json({ error: "Stripe customer failed", detail: customer }, 502);

  const ephemeralKey = await stripe(
    stripeKey,
    "POST",
    "ephemeral_keys",
    { customer: customer.id },
    { "Stripe-Version": "2024-06-20" }
  );

  const intent = await stripe(stripeKey, "POST", "payment_intents", {
    amount: String(amountCents),
    currency: "chf",
    customer: customer.id,
    "automatic_payment_methods[enabled]": "true",
    "metadata[booking_id]": booking.id,
    "metadata[user_id]": userId,
  });
  if (!intent.client_secret) {
    return json({ error: "PaymentIntent failed", detail: intent }, 502);
  }

  return json({
    clientSecret: intent.client_secret,
    ephemeralKey: ephemeralKey.secret,
    customer: customer.id,
    amount: amountCents,
    currency: "chf",
  });
});

async function stripe(
  key: string,
  method: "GET" | "POST",
  path: string,
  body?: Record<string, string | object>,
  extraHeaders: Record<string, string> = {}
): Promise<any> {
  const init: RequestInit = {
    method,
    headers: {
      Authorization: `Bearer ${key}`,
      "Content-Type": "application/x-www-form-urlencoded",
      ...extraHeaders,
    },
  };
  if (body) {
    const params = new URLSearchParams();
    for (const [k, v] of Object.entries(body)) {
      if (typeof v === "object" && v !== null) {
        for (const [kk, vv] of Object.entries(v as Record<string, unknown>)) {
          params.append(`${k}[${kk}]`, String(vv));
        }
      } else {
        params.append(k, String(v));
      }
    }
    init.body = params.toString();
  }
  const res = await fetch(`https://api.stripe.com/v1/${path}`, init);
  return res.json();
}

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

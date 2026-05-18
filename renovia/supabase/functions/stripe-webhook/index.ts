// Renovia — Edge Function "stripe-webhook"
// Recoit les events Stripe (verifie la signature) et flippe bookings.deposit_paid
// + status quand un PaymentIntent reussit.
//
// Important : declarer cette function en --no-verify-jwt pour qu'elle ne
// rejette pas les requetes de Stripe (Stripe n'envoie pas de JWT Supabase).
//
//   supabase functions deploy stripe-webhook --no-verify-jwt
//   supabase secrets set STRIPE_WEBHOOK_SECRET=whsec_xxx
//
// Endpoint a configurer cote Stripe (Dashboard → Developers → Webhooks) :
//   https://<project-ref>.supabase.co/functions/v1/stripe-webhook
// Events a ecouter : payment_intent.succeeded, payment_intent.payment_failed

import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.4";

Deno.serve(async (req) => {
  if (req.method !== "POST") return new Response("Method not allowed", { status: 405 });

  const secret = Deno.env.get("STRIPE_WEBHOOK_SECRET");
  const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
  if (!secret || !stripeKey) {
    return new Response("Webhook misconfigured", { status: 500 });
  }

  const signature = req.headers.get("stripe-signature");
  if (!signature) return new Response("Missing signature", { status: 400 });

  const payload = await req.text();
  const valid = await verifyStripeSignature(payload, signature, secret);
  if (!valid) return new Response("Invalid signature", { status: 400 });

  const event = JSON.parse(payload) as {
    type: string;
    data: { object: Record<string, unknown> };
  };

  const admin = createClient(
    Deno.env.get("SUPABASE_URL")!,
    Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
  );

  if (event.type === "payment_intent.succeeded") {
    const pi = event.data.object as {
      id: string;
      metadata?: Record<string, string>;
    };
    const bookingId = pi.metadata?.booking_id;
    if (bookingId) {
      const { error } = await admin
        .from("bookings")
        .update({ deposit_paid: true, status: "en_preparation" })
        .eq("id", bookingId);
      if (error) {
        console.error("update booking failed", error);
        return new Response("DB update failed", { status: 500 });
      }
    }
  } else if (event.type === "payment_intent.payment_failed") {
    const pi = event.data.object as {
      id: string;
      metadata?: Record<string, string>;
      last_payment_error?: { message?: string };
    };
    console.warn(
      "PaymentIntent failed",
      pi.id,
      pi.last_payment_error?.message,
      "booking:",
      pi.metadata?.booking_id
    );
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
});

// Verification HMAC-SHA256 du header Stripe-Signature (format :
//   t=<timestamp>,v1=<signature>,...)
async function verifyStripeSignature(
  payload: string,
  header: string,
  secret: string,
  toleranceSec = 300
): Promise<boolean> {
  const parts = Object.fromEntries(
    header.split(",").map((kv) => {
      const idx = kv.indexOf("=");
      return [kv.slice(0, idx), kv.slice(idx + 1)];
    })
  );
  const t = parts.t;
  const v1 = parts.v1;
  if (!t || !v1) return false;

  const age = Math.abs(Date.now() / 1000 - Number(t));
  if (age > toleranceSec) return false;

  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign"]
  );
  const sigBuf = await crypto.subtle.sign("HMAC", key, enc.encode(`${t}.${payload}`));
  const hex = Array.from(new Uint8Array(sigBuf))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return timingSafeEqual(hex, v1);
}

function timingSafeEqual(a: string, b: string): boolean {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

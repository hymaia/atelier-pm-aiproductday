/**
 * webhook_handler.ts — Gestion des webhooks sortants
 * Plateforme SaaS — API v2.3
 */

const MAX_RETRIES = 5;
const RETRY_DELAYS_MS = [1000, 5000, 30000, 300000, 1800000]; // 1s, 5s, 30s, 5min, 30min
const WEBHOOK_TIMEOUT_MS = 10000; // 10 secondes
const DEAD_LETTER_THRESHOLD = 5; // Après 5 échecs → dead letter queue

interface WebhookEvent {
  id: string;
  type: string;           // ex: "product.created", "order.updated"
  tenantId: string;
  payload: object;
  createdAt: Date;
}

interface WebhookDelivery {
  eventId: string;
  url: string;
  attempt: number;
  status: "pending" | "success" | "failed" | "dead_letter";
  responseCode?: number;
  error?: string;
  nextRetryAt?: Date;
}

/**
 * Envoie un événement webhook à l'URL configurée par le tenant.
 * 
 * Mécanisme de retry exponentiel :
 * - Tentative 1 : immédiat
 * - Tentative 2 : après 1 seconde
 * - Tentative 3 : après 5 secondes
 * - Tentative 4 : après 30 secondes
 * - Tentative 5 : après 5 minutes
 * - Tentative 6 : après 30 minutes → si échec, dead letter queue
 * 
 * Dead letter queue : les événements non livrés après 5 tentatives
 * sont conservés 7 jours et consultables via GET /webhooks/dead-letter
 */
async function deliverWebhook(
  event: WebhookEvent,
  targetUrl: string,
  attempt: number = 0
): Promise<WebhookDelivery> {
  
  const delivery: WebhookDelivery = {
    eventId: event.id,
    url: targetUrl,
    attempt,
    status: "pending",
  };

  try {
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Webhook-Event": event.type,
        "X-Webhook-Tenant": event.tenantId,
        "X-Webhook-Attempt": String(attempt + 1),
        "X-Webhook-Signature": generateSignature(event), // HMAC-SHA256
      },
      body: JSON.stringify(event.payload),
      signal: AbortSignal.timeout(WEBHOOK_TIMEOUT_MS),
    });

    if (response.ok) {
      delivery.status = "success";
      delivery.responseCode = response.status;
      return delivery;
    }

    // Réponse HTTP reçue mais code d'erreur (4xx, 5xx)
    delivery.responseCode = response.status;
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);

  } catch (error) {
    delivery.status = "failed";
    delivery.error = String(error);

    if (attempt >= MAX_RETRIES) {
      // Toutes les tentatives épuisées → dead letter queue
      delivery.status = "dead_letter";
      await sendToDeadLetterQueue(event, delivery);
      notifyTenantWebhookFailed(event.tenantId, event.id);
      return delivery;
    }

    // Planifier la prochaine tentative
    const delayMs = RETRY_DELAYS_MS[attempt] ?? RETRY_DELAYS_MS[RETRY_DELAYS_MS.length - 1];
    delivery.nextRetryAt = new Date(Date.now() + delayMs);
    await scheduleRetry(event, targetUrl, attempt + 1, delayMs);
    
    return delivery;
  }
}

/**
 * Envoie les événements non livrés dans la dead letter queue.
 * Conservés 7 jours, consultables via l'API ou le dashboard.
 */
async function sendToDeadLetterQueue(
  event: WebhookEvent,
  delivery: WebhookDelivery
): Promise<void> {
  await deadLetterStore.save({
    event,
    delivery,
    expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 jours
  });
}

function generateSignature(event: WebhookEvent): string {
  // HMAC-SHA256 du payload avec la clé secrète du tenant
  // Permet au client de vérifier l'authenticité de l'événement
  return hmacSHA256(JSON.stringify(event.payload), getTenantSecret(event.tenantId));
}

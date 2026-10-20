<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, type Proposal } from "../api";
import RiskBadge from "../components/RiskBadge.vue";
const text = ref(""),
  actor = ref(""),
  proposals = ref<Proposal[]>([]);
const loading = ref(true),
  busy = ref(false),
  error = ref("");
async function load() {
  proposals.value = await api<Proposal[]>("/agent-actions");
}
onMounted(async () => {
  try {
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
});
async function propose() {
  busy.value = true;
  error.value = "";
  try {
    await api("/agent/propose", "POST", { text: text.value });
    text.value = "";
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
async function decide(id: number, decision: string) {
  busy.value = true;
  error.value = "";
  try {
    await api(`/agent-actions/${id}/${decision}`, "POST", {
      decide_par: actor.value.trim(),
    });
    await load();
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="eyebrow">HUMAN-IN-THE-LOOP</div>
  <div class="page-heading">
    <div>
      <h1>Agent proposals</h1>
      <p>The agent proposes. You review and decide.</p>
    </div>
    <span class="status">Fake parser · no LLM</span>
  </div>
  <section class="panel composer">
    <h2>What would you like to order?</h2>
    <form @submit.prevent="propose">
      <label for="request">Order request</label>
      <div class="input-row">
        <input
          id="request"
          v-model="text"
          maxlength="2000"
          required
          placeholder="10 stylos pour Acme"
        /><button :disabled="busy || !text.trim()">
          {{ busy ? "Working…" : "Create proposal →" }}
        </button>
      </div>
    </form>
    <small
      >Use an exact product and client name. Creating a proposal does not create
      an order.</small
    >
  </section>
  <p v-if="error" class="error" role="alert">{{ error }}</p>
  <label class="reviewer"
    >Your name for the decision record<input
      v-model="actor"
      maxlength="200"
      placeholder="e.g. Alice"
      autocomplete="name"
  /></label>
  <p v-if="loading" role="status">Loading proposals…</p>
  <p v-else-if="!proposals.length" class="empty">
    No proposals yet. Start with an order request above.
  </p>
  <article
    v-for="proposal in proposals"
    :key="proposal.id"
    class="panel proposal"
  >
    <div class="proposal-heading">
      <h2>
        Proposal #{{ proposal.id }}
        <span class="status">{{ proposal.statut }}</span>
      </h2>
      <RiskBadge :score="proposal.risk_score" />
    </div>
    <div class="proposal-grid">
      <div>
        <h3>Proposed payload</h3>
        <pre>{{ JSON.stringify(proposal.payload, null, 2) }}</pre>
      </div>
      <div>
        <h3>Reasoning</h3>
        <p>{{ proposal.raisonnement }}</p>
        <h3>Risk explanation</h3>
        <p>{{ proposal.risk_explanation }}</p>
      </div>
    </div>
    <div v-if="proposal.statut === 'proposee'" class="actions">
      <small>Approval creates a validated order.</small
      ><button
        class="secondary"
        :disabled="busy || !actor.trim()"
        @click="decide(proposal.id, 'reject')"
      >
        Reject</button
      ><button
        :disabled="busy || !actor.trim()"
        @click="decide(proposal.id, 'approve')"
      >
        Approve & create order
      </button>
    </div>
    <div v-else class="decision">
      {{ proposal.statut }} by {{ proposal.decide_par }} ·
      {{ proposal.decide_le }}
      <RouterLink v-if="proposal.order_id" :to="`/orders/${proposal.order_id}`"
        >View order ↗</RouterLink
      >
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import { useRoute } from "vue-router";
import { api, money, total, type Order } from "../api";
import RiskBadge from "../components/RiskBadge.vue";
const route = useRoute();
const order = ref<Order | null>(null);
const loading = ref(false),
  busy = ref(false),
  error = ref(""),
  notice = ref("");
async function load() {
  loading.value = true;
  error.value = "";
  order.value = null;
  notice.value = "";
  try {
    order.value = await api<Order>(`/orders/${route.params.id}`);
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
}
watch(() => route.params.id, load, { immediate: true });
async function invoice() {
  if (!order.value) return;
  busy.value = true;
  error.value = "";
  try {
    const result = await api<{ id: number }>(
      `/orders/${order.value.id}/invoice`,
      "POST",
    );
    order.value = await api<Order>(`/orders/${order.value.id}`);
    notice.value = `Invoice #${result.id} generated.`;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <RouterLink class="back" to="/">← All orders</RouterLink>
  <p v-if="loading" role="status">Loading order…</p>
  <p v-if="error" class="error" role="alert">{{ error }}</p>
  <p v-if="notice" class="success" role="status">{{ notice }}</p>
  <template v-if="order"
    ><div class="page-heading">
      <div>
        <div class="eyebrow">ORDER DETAIL</div>
        <h1>Order #{{ String(order.id).padStart(4, "0") }}</h1>
        <p>
          Client #{{ order.contact_id }} · {{ order.date }} · {{ order.statut }}
        </p>
      </div>
      <button
        v-if="order.statut === 'validee'"
        :disabled="busy"
        @click="invoice"
      >
        {{ busy ? "Generating…" : "Generate invoice" }}
      </button>
    </div>
    <div class="detail-grid">
      <section class="panel">
        <div class="panel-title">Order lines</div>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Quantity</th>
                <th>Unit price</th>
                <th>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in order.lines" :key="line.id">
                <td>Product #{{ line.product_id }}</td>
                <td>{{ line.quantite }}</td>
                <td>{{ money(Number(line.prix_unitaire)) }}</td>
                <td>{{ money(line.quantite * Number(line.prix_unitaire)) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="total">
          Order total <strong>{{ money(total(order)) }}</strong>
        </div>
      </section>
      <aside class="panel risk-panel">
        <div class="eyebrow">RULE-BASED ASSESSMENT</div>
        <h2>Risk explanation</h2>
        <RiskBadge :score="order.risk_score" />
        <p>{{ order.risk_explanation }}</p>
        <small>Calculated when this order was created.</small>
      </aside>
    </div>
  </template>
</template>

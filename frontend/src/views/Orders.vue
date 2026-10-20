<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, total, money, type Order } from "../api";
import RiskBadge from "../components/RiskBadge.vue";
const orders = ref<Order[]>([]);
const loading = ref(true);
const error = ref("");
onMounted(async () => {
  try {
    orders.value = await api<Order[]>("/orders");
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="eyebrow">SALES WORKSPACE</div>
  <div class="page-heading">
    <div>
      <h1>Orders</h1>
      <p>A clear view of every order and the risk behind it.</p>
    </div>
    <RouterLink class="button" to="/proposals">＋ Propose an order</RouterLink>
  </div>
  <p v-if="error" class="error" role="alert">{{ error }}</p>
  <p v-if="loading" role="status">Loading orders…</p>
  <section v-else class="panel">
    <div class="panel-title">
      All orders <span class="count">{{ orders.length }}</span>
    </div>
    <div class="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Order</th>
            <th>Client</th>
            <th>Date</th>
            <th>Status</th>
            <th>Total</th>
            <th>Risk score</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="order in orders" :key="order.id">
            <td>
              <RouterLink :to="`/orders/${order.id}`"
                >#{{ String(order.id).padStart(4, "0") }} ↗</RouterLink
              >
            </td>
            <td>Client #{{ order.contact_id }}</td>
            <td>{{ order.date }}</td>
            <td>
              <span class="status">{{ order.statut }}</span>
            </td>
            <td>{{ money(total(order)) }}</td>
            <td><RiskBadge :score="order.risk_score" /></td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!orders.length" class="empty">
      No orders yet. Seed the sample data or approve an agent proposal.
    </p>
  </section>
  <p class="note">
    Risk scores follow fixed rules. Open an order to read its explanation.
  </p>
</template>

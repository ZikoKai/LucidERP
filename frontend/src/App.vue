<script setup lang="ts">
import { apiKey, saveKey } from "./api";
</script>

<template>
  <header class="topbar">
    <RouterLink class="brand" to="/"
      ><span class="mark">L</span> Lucid<span>ERP</span></RouterLink
    >
    <nav aria-label="Main navigation">
      <RouterLink to="/">Orders</RouterLink
      ><RouterLink to="/proposals">Agent proposals</RouterLink>
    </nav>
    <span class="version">LEARNING EDITION · V1</span>
  </header>
  <main>
    <details class="connection">
      <summary>API connection</summary>
      <label
        >Optional API key
        <input
          v-model="apiKey"
          type="password"
          autocomplete="off"
          @change="saveKey"
          placeholder="Only if API_KEY is set on the server" /></label
      ><small
        >Stored in this browser tab's session. Reload the screen after changing
        it.</small
      >
    </details>
    <RouterView />
  </main>
  <footer>LucidERP <span>Clear decisions. Human approval.</span></footer>
</template>

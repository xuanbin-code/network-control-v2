<template>
  <div class="flex h-screen bg-background">
    <AppSidebar />
    <main class="flex-1 overflow-auto bg-muted/30">
      <div class="p-8">
        <RouterView v-slot="{ Component }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </RouterView>
      </div>
    </main>
    <Sonner position="bottom-right" rich-colors close-button />
  </div>
</template>

<script setup lang="ts">
import AppSidebar from '@/components/layout/AppSidebar.vue'
import Sonner from '@/components/ui/sonner/Sonner.vue'
</script>

<style>
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(4px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>

<template>
  <div>
    <!-- Menu Hamburguer -->
    <nav class="navbar" v-if="componenteAtual !== 'MenuInicial'">
      <button class="menu-btn" @click="toggleMenu">☰</button>
    </nav>

    <!-- Overlay do menu -->
    <div v-if="menuAberto" class="menu-overlay" @click.self="menuAberto = false">
      <ul class="menu-list">
          <li @click="abrirComponente('AlertasBauru')">Alertas</li>
          <li @click="abrirComponente('MapaBauru')">Mapa histórico de acidentes</li>
          <li @click="abrirComponente('GraficoAcidentes')">Gráficos</li>
          <li @click="abrirComponente('MenuInicial')">Retornar ao menu</li>

      </ul>
    </div>

    <!-- Renderização condicional -->
    <component :is="componenteAtual" @navegar="abrirComponente"/>
  </div>
</template>

<script>
import MapaBauru from './components/MapaBauru.vue'
import GraficoAcidentes from './components/GraficoAcidentes.vue'
import AlertasBauru from './components/AlertasBauru.vue'
import MenuInicial from './components/MenuInicial.vue'

import "@/assets/app.css"


export default {
  name: 'App',
  components: {
    MapaBauru,
    GraficoAcidentes,
    AlertasBauru,
    MenuInicial
  },
  data() {
    return {
      componenteAtual: 'MenuInicial', // abre no menu inicial
      menuAberto: false
    }
  },
  methods: {
    toggleMenu() {
      this.menuAberto = !this.menuAberto
    },
    abrirComponente(componente) {
      this.componenteAtual = componente
      this.menuAberto = false
    }
  }
}
</script>

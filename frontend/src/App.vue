<template>
  <div>
    <!-- Menu Hamburguer -->
    <nav class="navbar">
      <button class="menu-btn" @click="toggleMenu">☰</button>
    </nav>

    <!-- Overlay do menu -->
    <div v-if="menuAberto" class="menu-overlay" @click.self="menuAberto = false">
      <ul class="menu-list">
        <li @click="abrirComponente('MapaBauru')">Mapa de Bauru</li>
        <li @click="abrirComponente('GraficoAcidentes')">Gráficos</li>
      </ul>
    </div>

    <!-- Renderização condicional do componente -->
    <component :is="componenteAtual" />
  </div>
</template>

<script>
import MapaBauru from './components/MapaBauru.vue'
import GraficoAcidentes from './components/GraficoAcidentes.vue'

export default {
  name: 'App',
  components: {
    MapaBauru,
    GraficoAcidentes
  },
  data() {
    return {
      componenteAtual: 'MapaBauru',
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

<style>
body {
  margin: 0;
  font-family: Arial, sans-serif;
}

.navbar {
  background: #333;
  padding: 10px;
  color: white;
  position: relative;
}

.menu-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: white;
  cursor: pointer;
}

/* Overlay do menu */
.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.95); /* preto quase opaco */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

/* Lista de opções centralizada */
.menu-list {
  list-style: none;
  margin: 0;
  padding: 0;
  text-align: center;
}

.menu-list li {
  font-size: 24px;
  padding: 20px 0;
  cursor: pointer;
  color: white;
  transition: color 0.3s;
}

.menu-list li:hover {
  color: #ffcc00;
}
</style>

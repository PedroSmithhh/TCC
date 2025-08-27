<template>
  <div class="menu-inicial">
    <h1>Bem-vindo ao SHIELD</h1>
    <p>Escolha uma das opções abaixo:</p>
    <ul>
        <li @click="$emit('navegar', 'AlertasBauru')">Alertas</li>
        <li @click="$emit('navegar', 'MapaBauru')">Mapa histórico de acidentes</li>
        <li @click="$emit('navegar', 'GraficoAcidentes')">Gráficos</li>

    </ul>
  </div>
</template>

<script>

import "@/assets/menuInicial.css"

export default {
  name: "MenuInicial"
}
</script>


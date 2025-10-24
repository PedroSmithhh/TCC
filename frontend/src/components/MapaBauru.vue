<template>
  <div id="map" style="height: 100vh;"></div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import Supercluster from 'supercluster';
import { point } from '@turf/helpers';

export default {
  name: 'MapaBauru',
  data() {
    return {
      map: null,
      clusterIndex: null, // O índice do supercluster
      markersLayer: L.layerGroup(), // Uma camada só para os marcadores
      pontosAcidentes: []
    };
  },
  mounted() {
    this.initMap();
    this.loadDataAndSetupClusters();
  },
  methods: {
    initMap() {
      this.map = L.map('map').setView([-22.3145, -49.0586], 13);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(this.map);
      this.markersLayer.addTo(this.map);

      // Eventos que disparam a atualização dos clusters
      this.map.on('moveend', this.updateMarkers);
    },

    loadDataAndSetupClusters() {
      fetch('/marcadores.json')
        .then(res => res.json())
        .then(dados => {
          // Formatar os dados para o padrão GeoJSON que o Supercluster entende
          this.pontosAcidentes = dados.map(ponto => {
            return point([ponto.lng, ponto.lat]);
          });

          // Inicializar o Supercluster
          this.clusterIndex = new Supercluster({
            radius: 100,       // Raio de agrupamento em pixels
            maxZoom: 17,      // Nível máximo de zoom para continuar clusterizando
            minZoom: 0
          });
          this.clusterIndex.load(this.pontosAcidentes); // Carrega os pontos

          // Renderizar os marcadores pela primeira vez
          this.updateMarkers();
        })
        .catch(err => {
          console.error('Erro ao carregar os marcadores:', err);
        });
    },

    updateMarkers() {
      if (!this.clusterIndex) return;

      const bounds = this.map.getBounds();
      const zoom = this.map.getZoom();

      // 4. Pedir ao Supercluster os clusters/pontos para a visão atual do mapa
      const clusters = this.clusterIndex.getClusters([
        bounds.getWest(),
        bounds.getSouth(),
        bounds.getEast(),
        bounds.getNorth()
      ], zoom);

      // Limpar os marcadores antigos e adicionar os novos
      this.markersLayer.clearLayers();

      clusters.forEach(cluster => {
        const [lng, lat] = cluster.geometry.coordinates;
        const properties = cluster.properties;

        // Se for um cluster (tem mais de 1 ponto)
        if (properties.cluster) {
          const pointCount = properties.point_count;
          const icon = this.createClusterIcon(pointCount);
          const marker = L.marker([lat, lng], { icon: icon });

          // Adiciona evento para dar zoom ao clicar
          marker.on('click', () => {
            const expansionZoom = this.clusterIndex.getClusterExpansionZoom(properties.cluster_id);
            this.map.setView([lat, lng], expansionZoom);
          });

          this.markersLayer.addLayer(marker);

        } else {
          // Se for um ponto único (acidente individual)
          // Renderizamos como um cluster de tamanho 1, como você queria.
          const icon = this.createClusterIcon(1);
          const marker = L.marker([lat, lng], { icon: icon });
          this.markersLayer.addLayer(marker);
        }
      });
    },

    // Função auxiliar para criar o ícone de círculo que você quer
    createClusterIcon(count) {
      let size = 'small';
      if (count >= 10 && count < 100) {
        size = 'medium';
      } else if (count >= 100) {
        size = 'large';
      }

      // A classe principal é 'marker-cluster' e a secundária define o tamanho/cor
      const className = `marker-cluster marker-cluster-${size}`;

      return L.divIcon({
        html: `<div><span>${count}</span></div>`,
        className: className, // Usando a classe corrigida
        iconSize: L.point(40, 40)
      });
    }
  }
}
</script>

<style>
/* Estilos principais para todos os clusters */
.marker-cluster {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%; /* Garante um círculo perfeito */
  font-weight: bold;
  font-family: "Helvetica Neue", Arial, Helvetica, sans-serif;
  color: #000;
  width: 40px;
  height: 40px;
}

/*
  O L.divIcon cria um ícone. Dentro dele, o nosso 'html' cria outra div.
  Este estilo garante que essa div interna se comporte como um círculo.
*/
.marker-cluster div {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 32px; /* Ligeiramente menor para criar o efeito de borda */
  height: 32px;
  border-radius: 50%;
}

.marker-cluster span {
  line-height: 1; /* Alinha o texto verticalmente com flexbox */
}

/* Cores para os diferentes tamanhos de cluster */
.marker-cluster-small {
  background-color: rgba(181, 226, 140, 0.6);
}
.marker-cluster-small div {
  background-color: rgba(110, 204, 57, 0.9);
}

.marker-cluster-medium {
  background-color: rgba(241, 211, 87, 0.6);
}
.marker-cluster-medium div {
  background-color: rgba(240, 194, 12, 0.9);
}

.marker-cluster-large {
  background-color: rgba(253, 156, 115, 0.6);
}
.marker-cluster-large div {
  background-color: rgba(241, 128, 23, 0.9);
}
</style>
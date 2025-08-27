<template>
  <div id="map" style="height: 100vh;"></div>
</template>

<script>
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster";
import "leaflet.markercluster/dist/MarkerCluster.css";
import "leaflet.markercluster/dist/MarkerCluster.Default.css";

export default {
  name: 'MapaBauru',
  mounted() {
    const map = L.map('map').setView([-22.3145, -49.0586], 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    const markerCluster = L.markerClusterGroup({
      spiderfyOnEveryZoom: true,
      showCoverageOnHover: true,
      zoomToBoundsOnClick: true,
      disableClusteringAtZoom: 17,
      maxClusterRadius: 50
    });

   fetch('/marcadores.json')
      .then(res => res.json())
      .then(dados => {
        dados.forEach(ponto => {
          L.marker([ponto.lat, ponto.lng]).addTo(markerCluster);
        });
        markerCluster.addTo(map);
      })
      .catch(err => {
        console.error('Erro ao carregar os marcadores:', err);
      });
  }
}
</script>

<style>
#map {
  width: 100%;
  height: 100%;
}
</style>

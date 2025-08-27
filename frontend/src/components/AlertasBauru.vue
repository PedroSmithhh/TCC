<template>
  <div id="map" style="height: 100vh; width: 100%;"></div>
</template>

<script>
import L from "leaflet"
import "leaflet/dist/leaflet.css"

export default {
  name: "AlertasBauru",
  data() {
    return {
      map: null,
      userMarker: null,
      arrowElement: null
    }
  },
  mounted() {
    this.initMap()
  },
  methods: {
    initMap() {
      // Inicializa o mapa em Bauru
      this.map = L.map("map").setView([-22.3145, -49.0587], 13)

      // Camada de tiles
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '© OpenStreetMap'
      }).addTo(this.map)

      // Geolocalização em tempo real
      if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
          pos => {
            const lat = pos.coords.latitude
            const lng = pos.coords.longitude
            const heading = pos.coords.heading // direção em graus

            // Se ainda não existe marcador, cria
            if (!this.userMarker) {
              const arrowIcon = L.divIcon({
                className: "user-arrow-icon",
                html: '<div class="arrow"></div>',
                iconSize: [30, 30],
                iconAnchor: [15, 15]
              })

              this.userMarker = L.marker([lat, lng], { icon: arrowIcon }).addTo(this.map)
              this.arrowElement = this.userMarker.getElement().querySelector(".arrow")

              // Centraliza no usuário e dá zoom
              this.map.setView([lat, lng], 18)
            } else {
              // Atualiza posição
              this.userMarker.setLatLng([lat, lng])
            }

            // Rotaciona a seta se heading existir
            if (heading !== null && !isNaN(heading) && this.arrowElement) {
              this.arrowElement.style.transform = `rotate(${heading}deg)`
            }
          },
          err => {
            console.error("Erro ao obter localização:", err)
            alert("Não foi possível obter sua localização.")
          },
          {
            enableHighAccuracy: true,
            maximumAge: 0
          }
        )
      } else {
        alert("Geolocalização não suportada pelo navegador.")
      }
    }
  }
}
</script>

<style>
/* Estilo da seta azul */
.user-arrow-icon .arrow {
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-bottom: 20px solid #007bff; /* azul */
  transform: rotate(0deg); /* rotação inicial */
  transition: transform 0.2s linear; /* suaviza a rotação */
}
</style>

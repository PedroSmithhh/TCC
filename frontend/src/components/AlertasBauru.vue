<template>
  <div id="map-container">
    <div id="map"></div>

    <!-- Botão central -->
    <button class="iniciar-btn" v-if="!monitorando" @click="abrirSelecaoVeiculo">
      Iniciar monitoramento
    </button>

    <!-- Modal de seleção de veículo -->
    <div v-if="mostrarSelecao" class="modal-overlay">
      <div class="modal-content">
        <h3>Selecione o tipo de veículo</h3>
        <ul class="lista-veiculos">
          <li v-for="(label, key) in tiposVeiculos" :key="key">
            <button class="veiculo-btn" @click="selecionarVeiculo(key)">
              {{ label }}
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
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
      arrowElement: null,
      risco: null,
      apiUrl: "http://localhost:8000/calcular_risco",
      monitorando: false,
      mostrarSelecao: false,
      tipoSelecionado: null,
      intervalId: null,
      tiposVeiculos: {
        tp_veiculo_automovel: "Automóvel",
        tp_veiculo_motocicleta: "Motocicleta",
        tp_veiculo_bicicleta: "Bicicleta",
        tp_veiculo_caminhao: "Caminhão",
        tp_veiculo_onibus: "Ônibus",
        tp_veiculo_outros: "Outros"
      }
    }
  },
  mounted() {
    this.initMap()
  },
  methods: {
    initMap() {
      this.map = L.map("map").setView([-22.3145, -49.0587], 13)
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap"
      }).addTo(this.map)
    },

    abrirSelecaoVeiculo() {
      this.mostrarSelecao = true
    },

    selecionarVeiculo(tipo) {
      this.tipoSelecionado = tipo
      this.mostrarSelecao = false
      this.monitorando = true
      this.iniciarGeolocalizacao()
    },

    iniciarGeolocalizacao() {
      if (!navigator.geolocation) {
        alert("Geolocalização não suportada pelo navegador.")
        return
      }

      navigator.geolocation.watchPosition(
        pos => {
          const lat = pos.coords.latitude
          const lng = pos.coords.longitude
          const heading = pos.coords.heading

          this.atualizarPosicao(lat, lng, heading)

          if (!this.intervalId) {
            this.consultarRisco(lat, lng)
            this.intervalId = setInterval(() => {
              this.consultarRisco(lat, lng)
            }, 30000)
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
    },

    atualizarPosicao(lat, lng, heading) {
      if (!this.userMarker) {
        const arrowIcon = L.divIcon({
          className: "user-arrow-icon",
          html: '<div class="arrow"></div>',
          iconSize: [30, 30],
          iconAnchor: [15, 15]
        })

        this.userMarker = L.marker([lat, lng], { icon: arrowIcon }).addTo(this.map)
        this.arrowElement = this.userMarker.getElement().querySelector(".arrow")
        this.map.setView([lat, lng], 18)
      } else {
        this.userMarker.setLatLng([lat, lng])
      }

      if (heading !== null && !isNaN(heading) && this.arrowElement) {
        this.arrowElement.style.transform = `rotate(${heading}deg)`
      }
    },

    async consultarRisco(lat, lng) {
      try {
        // Cria payload simplificado que a nossa nova API espera
        const payload = {
          latitude: lat, // Envia como NÚMERO
          longitude: lng, // Envia como NÚMERO
          tp_veiculo_selecionado: this.tipoSelecionado // Envia a STRING da chave do veículo
        }
        const res = await fetch(this.apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload) // Envia o novo payload simplificado
        })

        if (!res.ok) throw new Error(`Erro ${res.status}: ${res.statusText}`)

        const data = await res.json()
        this.risco = data.risco_estimado
        this.exibirRiscoNoMapa(this.risco, data.interpretacao)
      
      } catch (error) {
        console.error("Erro ao consultar risco:", error)
      }
    },

    exibirRiscoNoMapa(risco, interpretacao) {
      if (!this.arrowElement) return

      let cor = "#007bff"
      if (interpretacao === "MÉDIO") cor = "#ffcc00"
      if (interpretacao === "ALTO") cor = "#ff0000"

      this.arrowElement.style.borderBottomColor = cor

      if (this.userMarker) {
        this.userMarker
          .bindPopup(`Risco estimado: <b>${interpretacao}</b> (${(risco * 100).toFixed(1)}%)`)
          .openPopup()
      }
    }
  }
}
</script>

<style>
#map-container {
  position: relative;
  height: 100vh;
  width: 100%;
}
#map {
  height: 100%;
  width: 100%;
  z-index: 1;
}

/* Seta do usuário */
.user-arrow-icon .arrow {
  width: 0;
  height: 0;
  border-left: 12px solid transparent;
  border-right: 12px solid transparent;
  border-bottom: 20px solid #007bff;
  transform: rotate(0deg);
  transition: transform 0.2s linear, border-bottom-color 0.3s ease;
  z-index: 1000;
}

/* Botão */
.iniciar-btn {
  position: absolute;
  bottom: 10vh;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1001;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 20px;
  font-size: 16px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
}

.iniciar-btn:hover {
  background: #0056b3;
}
.lista-veiculos {
  list-style: none;
  padding: 0;    
  margin: 0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1002;
}
.modal-content {
  background: #fff;
  padding: 25px;
  border-radius: 10px;
  text-align: center;
  width: 300px;
}
.veiculo-btn {
  background: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  margin: 5px 0;
  padding: 10px 15px;
  width: 100%;
  cursor: pointer;
}
.veiculo-btn:hover {
  background: #0056b3;
}
</style>

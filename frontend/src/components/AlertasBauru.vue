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
      },
      audioContext: null,
      lastAlertAt: 0,
      alertCooldownMs: 10000,
      previousInterpretacao: null
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

      // inicializa o AudioContext no clique (necessário para tocar som)
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext
        if (!this.audioContext && AudioContext) this.audioContext = new AudioContext()
      } catch (e) {
        console.error("Erro ao inicializar áudio:", e)
      }

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
        const payload = {
          latitude: lat,
          longitude: lng,
          tp_veiculo_selecionado: this.tipoSelecionado
        }
        const res = await fetch(this.apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        })

        if (!res.ok) throw new Error(`Erro ${res.status}: ${res.statusText}`)

        const data = await res.json()
        this.risco = data.risco_estimado
        this.exibirRiscoNoMapa(this.risco, data.interpretacao)
      
      } catch (error) {
        console.error("Erro ao consultar risco:", error)
      }
    },

    playAlertSound(duration = 0.5, frequency = 880) {
      try {
        if (!this.audioContext) {
          const AudioContext = window.AudioContext || window.webkitAudioContext
          this.audioContext = new AudioContext()
        }

        const now = this.audioContext.currentTime
        const osc = this.audioContext.createOscillator()
        const gain = this.audioContext.createGain()

        osc.type = "sine"
        osc.frequency.setValueAtTime(frequency, now)
        gain.gain.setValueAtTime(0, now)
        gain.gain.linearRampToValueAtTime(0.9, now + 0.01)
        gain.gain.exponentialRampToValueAtTime(0.001, now + duration)

        osc.connect(gain)
        gain.connect(this.audioContext.destination)
        osc.start(now)
        osc.stop(now + duration)
      } catch (e) {
        console.error("Erro ao tentar reproduzir som de alerta:", e)
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

      // --- lógica do alerta sonoro ---
      const now = Date.now()
      const podeAlertar =
        interpretacao === "ALTO" &&
        (this.previousInterpretacao !== "ALTO" || now - this.lastAlertAt > this.alertCooldownMs)

      if (podeAlertar) {
        this.playAlertSound(0.6, 880)
        this.lastAlertAt = now
      }

      this.previousInterpretacao = interpretacao
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

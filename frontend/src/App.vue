<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { fetchProjectById, fetchProjects } from './apiClient'

const projects = ref([])
const selectedProject = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const mapError = ref('')

const mapContainerRef = ref(null)

const YMAPS_SCRIPT_ID = 'yandex-maps-v3-script'
const CITY_CENTER = [30.1282, 59.5684] // [lon, lat], Гатчина

let mapInstance = null
let ymaps3Entities = null
let markerEntities = []

function hasCoordinates(project) {
  return Number.isFinite(project?.location?.lat) && Number.isFinite(project?.location?.lon)
}

function getProjectCoords(project) {
  return [project.location.lon, project.location.lat]
}

function formatCoords(project) {
  if (!hasCoordinates(project)) {
    return 'координаты не указаны'
  }

  return `lat: ${project.location.lat}, lon: ${project.location.lon}`
}

function getMapsApiKey() {
  return import.meta.env.VITE_YMAPS_API_KEY || ''
}

function loadYandexMapsScript(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.ymaps3) {
      resolve(window.ymaps3)
      return
    }

    const existingScript = document.getElementById(YMAPS_SCRIPT_ID)
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(window.ymaps3))
      existingScript.addEventListener('error', () => reject(new Error('Не удалось загрузить Yandex Maps JS API v3')))
      return
    }

    const script = document.createElement('script')
    script.id = YMAPS_SCRIPT_ID
    script.src = `https://api-maps.yandex.ru/v3/?apikey=${encodeURIComponent(apiKey)}&lang=ru_RU`
    script.async = true
    script.onload = () => resolve(window.ymaps3)
    script.onerror = () => reject(new Error('Не удалось загрузить Yandex Maps JS API v3'))
    document.head.appendChild(script)
  })
}

async function initMap() {
  mapError.value = ''

  const apiKey = getMapsApiKey()
  if (!apiKey) {
    mapError.value = 'Не найден ключ Yandex Maps. Добавьте VITE_YMAPS_API_KEY в frontend/.env.local.'
    return
  }

  if (!mapContainerRef.value) {
    mapError.value = 'Не найден контейнер карты.'
    return
  }

  try {
    const ymaps3 = await loadYandexMapsScript(apiKey)
    await ymaps3.ready

    const { YMap, YMapMarker, YMapDefaultSchemeLayer, YMapDefaultFeaturesLayer } = ymaps3
    ymaps3Entities = { YMapMarker }

    mapInstance = new YMap(mapContainerRef.value, {
      location: {
        center: CITY_CENTER,
        zoom: 11,
      },
    })

    mapInstance.addChild(new YMapDefaultSchemeLayer())
    mapInstance.addChild(new YMapDefaultFeaturesLayer())

    renderMarkers()
  } catch (error) {
    console.error('Ошибка инициализации карты:', error)
    mapError.value = 'Не удалось инициализировать карту. Проверьте API-ключ и доступ к сети.'
  }
}

function clearMarkers() {
  if (!mapInstance || markerEntities.length === 0) {
    return
  }

  markerEntities.forEach((marker) => {
    mapInstance.removeChild(marker)
  })
  markerEntities = []
}

function buildMarkerElement(project, isSelected) {
  const markerElement = document.createElement('button')
  markerElement.type = 'button'
  markerElement.className = `project-marker ${isSelected ? 'project-marker--active' : ''}`
  markerElement.textContent = project.name?.[0] || '•'
  markerElement.title = project.name || 'Проект'
  markerElement.onclick = () => {
    handleMarkerClick(project)
  }
  return markerElement
}

function renderMarkers() {
  if (!mapInstance || !ymaps3Entities) {
    return
  }

  clearMarkers()

  const markers = projects.value.filter(hasCoordinates).map((project) => {
    const isSelected = selectedProject.value?.id === project.id

    return new ymaps3Entities.YMapMarker(
      { coordinates: getProjectCoords(project) },
      buildMarkerElement(project, isSelected),
    )
  })

  markers.forEach((marker) => mapInstance.addChild(marker))
  markerEntities = markers
}

async function handleMarkerClick(project) {
  selectedProject.value = project

  try {
    const fullProject = await fetchProjectById(project.id)
    selectedProject.value = fullProject
  } catch (error) {
    console.error('Не удалось загрузить детали проекта:', error)
  }
}

async function loadProjects() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const data = await fetchProjects()
    projects.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('Ошибка при загрузке проектов:', error)
    errorMessage.value = 'Не удалось загрузить проекты. Проверьте backend и попробуйте снова.'
    projects.value = []
  } finally {
    isLoading.value = false
  }
}

watch(projects, () => {
  renderMarkers()
})

watch(selectedProject, () => {
  renderMarkers()
})

onMounted(async () => {
  await loadProjects()
  await initMap()
})

onBeforeUnmount(() => {
  clearMarkers()

  if (mapInstance) {
    mapInstance.destroy()
    mapInstance = null
  }
})
</script>

<template>
  <main class="page">
    <h1>Интерактивная карта проектов</h1>

    <p v-if="isLoading">Загрузка проектов...</p>
    <p v-else-if="errorMessage">{{ errorMessage }}</p>

    <section v-else class="layout">
      <div class="map-panel">
        <p v-if="mapError" class="map-error">{{ mapError }}</p>
        <div ref="mapContainerRef" class="map-container" />
      </div>

      <aside class="info-panel">
        <h2>Проекты на карте: {{ projects.length }}</h2>
        <p v-if="selectedProject">
          Выбран проект: <strong>{{ selectedProject.name || selectedProject.id }}</strong><br />
          Категория: {{ selectedProject.category || 'без категории' }}<br />
          Координаты: {{ formatCoords(selectedProject) }}
        </p>
        <p v-else>Кликните по маркеру на карте, чтобы выбрать проект.</p>
      </aside>
    </section>
  </main>
</template>
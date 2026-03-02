<script setup>
import { onMounted, ref } from 'vue'
import { fetchProjects } from './apiClient'

const projects = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

function formatCoords(project) {
  const lat = project?.location?.lat
  const lon = project?.location?.lon

  if (lat == null || lon == null) {
    return 'координаты не указаны'
  }

  return `lat: ${lat}, lon: ${lon}`
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

onMounted(loadProjects)
</script>

<template>
  <main>
    <h1>Список проектов</h1>

    <p v-if="isLoading">Загрузка проектов...</p>
    <p v-else-if="errorMessage">{{ errorMessage }}</p>

    <div v-else>
      <p>Всего проектов: {{ projects.length }}</p>
      <ul>
        <li v-for="project in projects" :key="project.id">
          <strong>{{ project.name || 'Без названия' }}</strong>
          — {{ project.category || 'без категории' }}
          — {{ formatCoords(project) }}
        </li>
      </ul>
    </div>
  </main>
</template>

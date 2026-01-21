<template>
  <div class="container">
    <h1>web crawler</h1>

    <div class="search-section">
      <input 
        v-model="config.url" 
        type="text" 
        placeholder="url do site (do tipo: https://google.com)" 
      />
      <input 
        v-model="config.palavra" 
        type="text" 
        placeholder="palavra a procurar" 
      />
      <input 
        v-model="config.profundidade" 
        type="text" 
        placeholder="profundidade" 
      />
      <input
        v-model="config.date"
        type="date"
      />
      <input
        v-model="config.time"
        type="time"
      />
      <button @click="executarCrawl" :disabled="loading">
        {{ loading ? 'a processar' : 'iniciar crawl' }}
      </button>
    </div>

    

    <div class="crawl-requests">
      <h2>pedidos de crawl</h2>
      <button @click="carregarHistorico" class="botao-refresh">atualizar lista</button>

      <table>
        <thead>
          <tr>
            <th>id</th>
            <th>url</th>
            <th>palavra</th>
            <th>profundidade</th>
            <th>status</th>
            <th>data de execução</th>
            <th>hora de execução</th>
            <th>remover</th>
          </tr>
          
        </thead>
        <tbody>
          <tr v-for="item in historico" :key="item.id">
            <td>{{ item.id }}</td>
            <td>{{ item.url }}</td>
            <td>{{ item.palavra }}</td>
            <td>{{ item.profundidade }}</td>
            <td>{{ item.status }}</td>
            <td>{{ item.data_execucao }}</td>
            <td>{{ item.hora_execucao }}</td>
            <td><button @click="removerCrawl(item.id)">remover</button></td>
          </tr>
          <tr v-if="historico.length === 0">
            <td colspan="8" style="text-align: center;">nenhum pedido encontrado</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class = "log-section">
      <h2>Logs de execução</h2>
      <button @click="carregarLogs" class="botao-refresh">atualizar lista</button>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Data execução</th>
            <th>Palavra</th>
            <th>Link</th>
            <th>ID do pedido</th>
            <th>Contagem</th>
          </tr>
          
        </thead>
        <tbody>
          <tr v-for="item in logs" :key="logs.id">
            <td>{{ item.id }}</td>
            <td>{{ item.data_execucao }}</td>
            <td>{{ item.palavra }}</td>
            <td>
              <a :href="item.link" target="_blank" class="table-link">
                {{ item.link }}
              </a>
            </td>
            <td>{{ item.pedido_id }}</td>
            <td>{{ item.contagem }}</td>
          </tr>
          <tr v-if="logs.length === 0">
            <td colspan="6" style="text-align: center;">nenhum log encontrado.</td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const config = ref({ 
  url: '', 
  palavra: '', 
  profundidade: '',
  date: '',
  time: '',
})
const historico = ref([])
const logs = ref([])
const loading = ref(false)

// const paginaHistorico = ref(1)
// const paginaLogs = ref(1)
// const itensPorPagina = 10

// const historicoPaginado = computed(() => {
//   const inicio = (paginaHistorico.value - 1) * itensPorPagina
//   const fim = inicio + itensPorPagina
//   return historico.value.slice(inicio, fim)
// })

// const logsPaginados = computed(() => {
//   const inicio = (paginaLogs.value - 1) * itensPorPagina
//   const fim = inicio + itensPorPagina
//   return logs.value.slice(inicio, fim)
// })

// const totalPaginasHistorico = computed(() => Math.ceil(historico.value.length / itensPorPagina))
// const totalPaginasLogs = computed(() => Math.ceil(logs.value.length / itensPorPagina))

//chama o backend
const executarCrawl = async () => {
  if (!config.value.url || !config.value.palavra || !config.value.profundidade || !config.value.date || !config.value.time) {
    alert("preencha os campos TODOS")
    return
  }

  loading.value = true
  try {
    await axios.post('http://localhost:8000/crawl', config.value)
    alert("crawl finalizado")
    config.value.url = ''
    config.value.palavra = ''
    config.value.profundidade = ''
    config.value.date = ''
    carregarHistorico()
  } catch (error) {
    console.error("erro ao fazer crawl ", error)
    alert("erro ao comunicar com o sv")
  } finally {
    loading.value = false
  }
}

const carregarHistorico = async () => {
  try {
    const response = await axios.get('http://localhost:8000/crawl')
    historico.value = response.data
  } catch (error) {
    console.error("Erro ao carregar histórico:", error)
  }
}

const carregarLogs = async () => {
  try {
    const response = await axios.get('http://localhost:8000/logs')
    logs.value = response.data
  } catch (error) {
    console.error("erro ao carregar os logs:", error)
  }
}

const removerCrawl = async (id) => {
  try {
    await axios.delete(`http://localhost:8000/crawl/${id}`)
    alert("crawl removido!")
    carregarHistorico()
  } catch (error) {
    console.error("erro ao remover crawl:", error)
    alert("erro ao comunicar com o sv")
  }
}

//da load assim que inicia
onMounted(carregarHistorico)
</script>

<style scoped>
.container {
  max-width: 900px;
  margin: 0 auto;
  font-family: sans-serif;
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

button {
  padding: 10px 20px;
  background-color: #e21f1f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

td {
  border: 1px solid #ffffff;
  padding: 12px;
  text-align: left;
  max-width: 400px;
  word-break: break-all;
  overflow-wrap: break-word;
  font-size: 13px;
}

th {
  border: 1px solid #ffffff;
  padding: 12px;
  text-align: left;
  max-width: 400px;
  background-color: #e21f1f;
}



.botao-refresh {
  background-color: #35495e;
  margin-bottom: 10px;
}
</style>
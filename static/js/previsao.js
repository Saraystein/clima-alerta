document.addEventListener('DOMContentLoaded', function () {
  const cardsDia = document.querySelectorAll('.card-dia');
  const dados = window.dadosPrevisao;
  const hojeStr = new Date().toISOString().split("T")[0];

  // Exibir "Hoje" visualmente no card correto
  cardsDia.forEach(card => {
    const dia = card.getAttribute('data-dia');
    if (dia === hojeStr) {
      const label = card.querySelector('h6');
      if (label) label.textContent = "Hoje";
    }
  });

  // Cria o gráfico com labels fixos
  inicializarGraficoPadrao();

  cardsDia.forEach(card => {
    card.addEventListener('click', function () {
      const diaClicado = this.getAttribute('data-dia'); // formato YYYY-MM-DD

      const diaSelecionado = dados.filter(item =>
        item.dt_txt && item.dt_txt.startsWith(diaClicado)
      );

      if (diaSelecionado.length > 0) {
        const primeiro = diaSelecionado[0];

        document.getElementById('temp-principal').innerText = primeiro.main.temp.toFixed(1) + '°C';
        document.getElementById('descricao-principal').innerText =
          primeiro.weather[0].description.charAt(0).toUpperCase() +
          primeiro.weather[0].description.slice(1);
        document.getElementById('icone-principal').src = `https://openweathermap.org/img/wn/${primeiro.weather[0].icon}@2x.png`;

        const tempMax = Math.max(...diaSelecionado.map(item => item.main.temp_max));
        const tempMin = Math.min(...diaSelecionado.map(item => item.main.temp_min));
        const umidade = diaSelecionado.reduce((acc, item) => acc + item.main.humidity, 0) / diaSelecionado.length;
        const vento = diaSelecionado.reduce((acc, item) => acc + item.wind.speed, 0) / diaSelecionado.length * 3.6;

        document.getElementById('temp-max').innerText = tempMax.toFixed(1) + '°C';
        document.getElementById('temp-min').innerText = tempMin.toFixed(1) + '°C';
        document.getElementById('umidade').innerText = umidade.toFixed(0) + '%';
        document.getElementById('vento').innerText = vento.toFixed(1) + ' km/h';

        atualizarGraficoComPadrao(diaSelecionado);
      }
    });
  });
});

// Define os horários fixos do gráfico
const horariosPadrao = ["00:00", "03:00", "06:00", "09:00", "12:00", "15:00", "18:00", "21:00"];

function inicializarGraficoPadrao() {
  const ctx = document.getElementById('graficoClima').getContext('2d');
  const temperaturasVazias = Array(horariosPadrao.length).fill(null);

  window.graficoClima = new Chart(ctx, {
    type: 'line',
    data: {
      labels: horariosPadrao,
      datasets: [{
        label: 'Temp (°C)',
        data: temperaturasVazias,
        backgroundColor: 'rgba(13, 110, 253, 0.2)',
        borderColor: 'rgba(13, 110, 253, 1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
}

function atualizarGraficoComPadrao(dadosDia) {
  const tempPorHorario = {};

  dadosDia.forEach(item => {
    const hora = item.dt_txt.split(' ')[1].substring(0, 5);
    tempPorHorario[hora] = item.main.temp;
  });

  const novaTemperatura = horariosPadrao.map(hora => tempPorHorario[hora] ?? null);

  window.graficoClima.data.datasets[0].data = novaTemperatura;
  window.graficoClima.update();
}

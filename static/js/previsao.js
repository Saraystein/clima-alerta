document.addEventListener('DOMContentLoaded', function () {
  const cardsDia = document.querySelectorAll('.card-dia');
  const dados = window.dadosPrevisao;

  cardsDia.forEach(card => {
    card.addEventListener('click', function () {
      const diaClicado = this.getAttribute('data-dia'); // dd/mm
      const [dia, mes] = diaClicado.split('/');
      const dataAlvo = `2025-${mes}-${dia.padStart(2, '0')}`;

      const diaSelecionado = dados.filter(item =>
        item.dt_txt.startsWith(dataAlvo)
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

        document.getElementById('temp-max').innerText = tempMax.toFixed(1);
        document.getElementById('temp-min').innerText = tempMin.toFixed(1);
        document.getElementById('umidade').innerText = umidade.toFixed(0);
        document.getElementById('vento').innerText = vento.toFixed(1);

        atualizarGraficoNovo(diaSelecionado);
      }
    });
  });
});

function atualizarGraficoNovo(dadosDia) {
  const container = document.getElementById('containerGrafico');
  container.innerHTML = '<canvas id="graficoClima"></canvas>';

  const ctx = document.getElementById('graficoClima').getContext('2d');
  const horarios = dadosDia.map(item => item.dt_txt.split(' ')[1].substring(0, 5));
  const temperaturas = dadosDia.map(item => item.main.temp);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: horarios,
      datasets: [{
        label: 'Temp (°C)',
        data: temperaturas,
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

document.addEventListener('DOMContentLoaded', function() {
  const inputCidade = document.querySelector('input[name="cidade"]');
  const listaSugestoes = document.createElement('div');
  listaSugestoes.setAttribute('id', 'autocomplete-list');
  listaSugestoes.setAttribute('class', 'list-group position-absolute w-100');
  inputCidade.parentNode.appendChild(listaSugestoes);

  let timeout = null;

  inputCidade.addEventListener('input', function() {
    clearTimeout(timeout);
    const termo = this.value.trim();

    if (termo.length < 2) {
      listaSugestoes.innerHTML = '';
      return;
    }

    timeout = setTimeout(() => {
      buscarCidades(termo);
    }, 300); // Espera 300ms depois de digitar
  });

  function buscarCidades(termo) {
    const url = `https://wft-geo-db.p.rapidapi.com/v1/geo/cities?namePrefix=${encodeURIComponent(termo)}&limit=5&sort=-population`;

    fetch(url, {
      method: 'GET',
      headers: {
        'X-RapidAPI-Key': 'e1d240be3amsh672e5ff103ec5aap106a9ajsneb5dc3868b8a',
        'X-RapidAPI-Host': 'wft-geo-db.p.rapidapi.com'
      }
    })
    .then(response => response.json())
    .then(data => {
      listaSugestoes.innerHTML = '';
      if (data.data) {
        data.data.forEach(cidade => {
          const item = document.createElement('button');
          item.type = 'button';
          item.classList.add('list-group-item', 'list-group-item-action');
          item.textContent = `${cidade.city}, ${cidade.country}`;
          item.addEventListener('click', () => {
            inputCidade.value = cidade.city;
            listaSugestoes.innerHTML = '';
          });
          listaSugestoes.appendChild(item);
        });
      }
    })
    .catch(error => {
      console.error('Erro ao buscar cidades:', error);
    });
  }
});

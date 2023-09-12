// we put this in a separate file to use the defer attr
new Chart(document.getElementById('myChart'), {
  type: 'line',
  data: {
    labels: [
      '2023-04',
      '2023-05',
      '2023-06',
      '2023-07',
      '2023-08',
      '2023-09',
      '2023-10'
    ],
    datasets: [{
      data: [
        39,
        42,
        38,
        35,
        40,
        41,
        29
      ],
      lineTension: 0,
      backgroundColor: 'transparent',
      borderColor: '#007bff',
      borderWidth: 4,
      pointBackgroundColor: '#007bff'
    }]
  },
  options: {
    scales: {
      // yAxes: [{
      //   ticks: {
      //     beginAtZero: false
      //   }
      // }]
    },
    plugins: {
      title: {
        display: false
      },
      legend: {
        display: false,
      }
    }
  }
})

// eslint-disable-next-line no-unused-vars
new Chart(document.getElementById("bar-chart"), {
  type: 'bar',
  data: {
    labels: [
      '2023-04',
      '2023-05',
      '2023-06',
      '2023-07',
      '2023-08',
      '2023-09',
      '2023-10'
    ],
    datasets: [{
      data: [
        6,
        5,
        4,
        15,
        7,
        8,
        9
      ],
      lineTension: 0,
      backgroundColor: '#007bff',
      borderColor: '#007bff',
      borderWidth: 4,
      pointBackgroundColor: '#007bff'
    }]
  },
  options: {
    scales: {
      // yAxes: [{
      //   ticks: {
      //     beginAtZero: false
      //   }
      // }]
    },
    plugins: {
      title: {
        display: false
      },
      legend: {
        display: false,
      }
    }
  }
})

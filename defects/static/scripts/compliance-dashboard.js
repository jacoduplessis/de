
    const weeks = Array(25).fill(0).map((v, i) => 'Week ' + (i + 1))

    const randInt = function (min, max) {
      const val = min + (max - min) * Math.random()
      return Math.floor(val)
    }

    const lineData = {
      labels: weeks,
      datasets: [{
        label: 'UG 2 #1',
        data: Array(weeks.length).fill(0).map(() => randInt(0, 50)),
        backgroundColor: 'red',
        borderColor: 'red',
      },
        {
          label: 'UG 2 #2',
          data: Array(weeks.length).fill(0).map(() => randInt(0, 50)),
          backgroundColor: 'blue',
          borderColor: 'blue',
        },
        {
          label: 'Merensky',
          data: Array(weeks.length).fill(0).map(() => randInt(0, 50)),
          backgroundColor: 'purple',
          borderColor: 'purple',
        }
      ]
    }

    const ctx = document.getElementById('line-chart')

    const lineChart = new Chart(ctx, {
      type: 'line',
      data: lineData,
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: false,
          }
        }
      }
    })


    const barCtx = document.getElementById('bar-chart')


    const barData = {
      labels: [
        'UG2 #1',
        'UG2 #2',
        'Merensky',
      ],

      datasets: [
        {
          label: 'In Progress',
          data: [14, 28, 20],
          borderColor: 'blue',
          backgroundColor: 'blue'
        },
        {
          label: 'Completed',
          data: [30, 12, 24],
          borderColor: 'green',
          backgroundColor: 'green',
        },
        {
          label: 'Outstanding',
          data: [4, 2, 7],
          borderColor: 'red',
          backgroundColor: 'red'
        }
      ]
    }

    const barConfig = {
      type: 'bar',
      data: barData,
      options: {
        indexAxis: 'y',
        // Elements options apply to all of the options unless overridden in a dataset
        // In this case, we are setting the border of each horizontal bar to be 2px wide
        elements: {
          bar: {
            borderWidth: 2,
          }
        },
        responsive: true,
        plugins: {
          legend: {
            position: 'top',
          },
          title: {
            display: false,
          }
        }
      },
    };

    const barChart = new Chart(barCtx, barConfig)

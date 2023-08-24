    (() => {
      // Graphs
      const ctx = document.getElementById('myChart')
      const ctxYear = document.getElementById('myChartYear')


      const labels = Array(52).fill(0).map((x, ix) => {
        return 'Week ' + ix
      })
      labels.push('Total')

      const monthLabels = [
        '2021-01',
        '2021-02',
        '2021-03',
        '2021-04',
        '2021-05',
        '2021-06',
        '2021-07',
        '2021-08',
        '2021-09',
        '2021-10',
        '2021-11',
        '2021-12',
        '2022-01',
        '2022-02',
        '2022-03',
        '2022-04',
        '2022-05',
        '2022-06',
        '2022-07',
        '2022-08',
        '2022-09',
        '2022-10',
        '2022-11',
        '2022-12',
        '2023-01',
        '2023-02',
        '2023-03',
        '2023-04',
        '2023-05',
        '2023-06',
        '2023-07',
        '2023-08',
        '2023-09',
        '2023-10',
        '2023-11',
        '2023-12',


      ]

      const randInt = function (min, max) {
        const val = min + (max - min) * Math.random()
        return Math.floor(val)
      }


      function waterfallSeries(n, min, max) {
        const deltas = Array(n).fill(0).map(x => randInt(min, max))
        const totals = Array(n).fill(0)
        const series = deltas.map((d, ix) => {
          if (ix === 0) {
            totals[0] = d
            return [0, d]
          }
          const prevEnd = totals[ix - 1]
          const newEnd = prevEnd + d
          totals[ix] = newEnd
          return [prevEnd, newEnd]
        })
        series.push([totals[totals.length - 1], 0])
        return series
      }

      const myChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: labels,
          datasets: [{
            label: 'Value',
            data: waterfallSeries(labels.length - 1, -100, 200),
            backgroundColor: function (ctx) {
              if (ctx.dataIndex === labels.length - 1) return 'blue'
              const [begin, end] = ctx.raw
              if (begin > end) return 'red'
              return 'green'
            }
          }]
        },
        options: {
          /* scales: {
             yAxes: [{
               ticks: {
                 beginAtZero: false
               }
             }]
           }, */
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      })

      const yearChart = new Chart(ctxYear, {
        type: 'bar',
        data: {
          labels: monthLabels,
          datasets: [{
            label: 'Value',
            data: waterfallSeries(monthLabels.length - 1, -100, 200),
            backgroundColor: function (ctx) {
              if (ctx.dataIndex === monthLabels.length - 1) return 'blue'
              const [begin, end] = ctx.raw
              if (begin > end) return 'red'
              return 'green'
            }
          }]
        },
        options: {
          /* scales: {
             yAxes: [{
               ticks: {
                 beginAtZero: false
               }
             }]
           }, */
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      })


    })()

    (() => {
      // Graphs

      const ctxWeek = document.getElementById('weekChart')
      const ctxMonth = document.getElementById('monthChart')
      const graphData = JSON.parse(document.getElementById("graph-data").textContent)

      const weekLabels = graphData.week_labels
      weekLabels.push("Total")

      const monthLabels = graphData.month_labels
      monthLabels.push("Total")

      function waterfallSeries(deltas) {
        const n = deltas.length
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

      const weekChart = new Chart(ctxWeek, {
        type: 'bar',
        data: {
          labels: weekLabels,
          datasets: [{
            label: 'Value',
            data: waterfallSeries(graphData.week_deltas),
            backgroundColor: function (ctx) {
              if (ctx.dataIndex === weekLabels.length - 1) return 'blue'
              const [begin, end] = ctx.raw
              if (begin > end) return 'red'
              return 'green'
            }
          }]
        },
        options: {
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      })

      const monthChart = new Chart(ctxMonth, {
        type: 'bar',
        data: {
          labels: monthLabels,
          datasets: [{
            label: 'Value',
            data: waterfallSeries(graphData.month_deltas),
            backgroundColor: function (ctx) {
              if (ctx.dataIndex === monthLabels.length - 1) return 'blue'
              const [begin, end] = ctx.raw
              if (begin > end) return 'red'
              return 'green'
            }
          }]
        },
        options: {
          plugins: {
            legend: {
              display: false,
            }
          }
        }
      })
    })()

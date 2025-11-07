
    const weeks = Array(52).fill(0).map((v, i) => 'Week ' + (i + 1))

    const sectionStats = JSON.parse(document.getElementById("section-stats").textContent)

    const riDatasets = Object.values(sectionStats).map(section => {
      return {
        label: section.name,
        data: section.ri_count_by_week.map(row => row.cnt)
      }
    })

    const lineData = {
      labels: weeks,
      datasets: riDatasets
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
      labels: Object.values(sectionStats).map(section => section.name),

      datasets: [
        {
          label: 'Completed',
          data: Object.values(sectionStats).map(s => s.solution_count_closed),
          borderColor: 'green',
          backgroundColor: 'green',
        },
        {
          label: 'Scheduled',
          data: Object.values(sectionStats).map(s => s.solution_count_scheduled),
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

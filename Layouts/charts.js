const support_color = "#aaa"; // color for axis labels and ticks

var CC = { // All charts
  'army': null,
  'supply': null,
  'killed': null,
  'mining': null
}


function generate_config(replay_data, x_data, type) {
  // generates config for a chart based on new data
  let c_title;
  if (type == 'army') c_title = 'Army value';
  if (type == 'supply') c_title = 'Supply used';
  if (type == 'killed') c_title = 'Kill count';
  if (type == 'mining') c_title = 'Resource collection rate';

  let data = {
    labels: x_data,
    datasets: [
      {
        data: replay_data[1][type],
        label: replay_data[1]['name'],
        borderColor: gP1Color,
      },
      {
        data: replay_data[2][type],
        label: replay_data[2]['name'],
        borderColor: gP2Color,
      }
    ]
  };

  let config = {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      events: [], //on which events the chart reacts (none here)
      datasets: {
        line: {
          pointRadius: 0 // disable for all point drawing
        }
      },
      plugins: {
        legend: {
          display: false,
          labels: {
            color: 'white', // legend color
          }
        },
        title: {
          display: true,
          fullSize: false, //center just above data area
          text: c_title,
          color: '#ddd',
          font: {
            family: 'Eurostile',
            size: 16
          },
          padding: {
            top: 10,
            bottom: 7
          }
        },
      },
      scales: {
        x: {
          display: true,
          title: {
            display: false,
          },
          ticks: {
            color: support_color,
          },
          grid: {
            color: '#333',
            borderColor: support_color,
            tickColor: support_color
          }
        },
        y: {
          display: true,
          grid: {
            color: '#333',
            borderColor: support_color,
            tickColor: support_color,
          },
          title: {
            display: false,
          },
          ticks: {
            color: support_color
          }
        }
      }
    }
  }
  return config
}

function update_chart(chart, replay_data, x_data, type) {
  // Updates an existing chart with new data
  chart.data.datasets[0].data = replay_data[1][type];
  chart.data.datasets[1].data = replay_data[2][type];
  chart.data.datasets[0].label = replay_data[1]['name'];
  chart.data.datasets[1].label = replay_data[2]['name'];
  chart.data.labels = x_data;
  chart.update()
}


function plot_chart(replay_data, x_data, type) {
  if (CC[type] == null) {
    // Either create new 
    let config = generate_config(replay_data, x_data, type);
    let chart_name = type + 'Chart';
    let ctx = document.getElementById(chart_name).getContext('2d');
    CC[type] = new Chart(ctx, config);
  } else {
    // Or update existing
    update_chart(CC[type], replay_data, x_data, type)
  }
}


function plot_charts(replay_data) {
  // Generate x_data (every 10s)
  let x_data = [];
  for (let i = 0; i < replay_data[1]['army'].length; i++) {
    x_data.push(format_length(i * 10, multiply = false));
  }
  // Plot all charts (or update)
  for (let key of Object.keys(CC)) {
    plot_chart(replay_data, x_data, key);
  }
}


function update_charts_colors(p1color, p2color) {
  // Updates charts with new colors for player 1 and 2
  if (CC.army == null) return;
  for (let key of Object.keys(CC)) {
    CC[key].data.datasets[0].borderColor = p1color;
    CC[key].data.datasets[1].borderColor = p2color;
    CC[key].update()
  }
}
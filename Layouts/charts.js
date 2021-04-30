const support_color = "#aaa"; // color for axis labels and ticks
var armyChart = null;
var killedChart = null;
var miningChart = null;


function generate_config(replay_data, x_data, type) {
  // generates config for a chart based on new data
  let c_title;
  if (type == 'army') c_title = 'Army value';
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
  chart.data.datasets[0].data = replay_data[1][type];
  chart.data.datasets[1].data = replay_data[2][type];
  chart.data.datasets[0].label = replay_data[1]['name'];
  chart.data.datasets[1].label = replay_data[2]['name'];
  chart.data.labels = x_data;
  chart.update()
}


function plot_chart(replay_data, x_data, type) {
  let config = generate_config(replay_data, x_data, type);
  let chart_name = type + 'Chart';
  let ctx = document.getElementById(chart_name).getContext('2d');

  // Either create a new chart or update it with new config
  if (type == 'army') {
    if (armyChart == null) armyChart = new Chart(ctx, config);
    else update_chart(armyChart, replay_data, x_data, type)
  }
  if (type == 'killed') {
    if (miningChart == null) miningChart = new Chart(ctx, config);
    else update_chart(miningChart, replay_data, x_data, type)
  }
  if (type == 'mining') {
    if (killedChart == null) killedChart = new Chart(ctx, config);
    else update_chart(killedChart, replay_data, x_data, type)
  }
}


function plot_charts(replay_data) {
  // Generate x_data (every 10s)
  let x_data = [];
  for (let i = 0; i < replay_data[1]['army'].length; i++) {
    x_data.push(format_length(i * 10, multiply = false));
  }
  // Plot
  plot_chart(replay_data, x_data, 'army');
  plot_chart(replay_data, x_data, 'killed');
  plot_chart(replay_data, x_data, 'mining');
}


function update_charts_colors(p1color, p2color) {
  // Updates charts with new colors for player 1 and 2
  if (armyChart == null) return;
  armyChart.data.datasets[0].borderColor = p1color;
  armyChart.data.datasets[1].borderColor = p2color;
  armyChart.update()
  miningChart.data.datasets[0].borderColor = p1color;
  miningChart.data.datasets[1].borderColor = p2color;
  miningChart.update()
  killedChart.data.datasets[0].borderColor = p1color;
  killedChart.data.datasets[1].borderColor = p2color;
  killedChart.update()
}
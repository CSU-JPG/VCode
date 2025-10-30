document.addEventListener('DOMContentLoaded', function () {
    let chartData;
    const COLORS = {
        general: 'rgba(13, 110, 253, 0.5)',
        unknown: 'rgba(220, 53, 69, 0.6)'
    };
    const chartDom = document.getElementById('chart');
    const myChart = echarts.init(chartDom);
    let currentBenchmark = 'vcode_overall', currentSubMetric = 'avg', currentView = 'recommendation';
    const subMetricGroup = document.getElementById('subMetricGroup');
    const subMetricsMap = { vcode_overall: [], general: ['avg', 'rec', 'ocr', 'know', 'gen', 'spat', 'math'], 
    professional: ['avg'], vision_centric: ['avg', '2d', '3d'] };
    const baseTooltipStyle = { backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#ccc', borderWidth: 1, textStyle: { color: '#333' }, padding: [10, 15] };

    let sortState = {
        key: 'vcode_overall',
        order: 'desc'
    };
    fetch('data/leaderboard_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.json();
        })
        .then(data => {
            chartData = data; 
            initializePage(); 
        })
        .catch(error => {
            console.error('Failed to load or parse data.json:', error);
            chartDom.innerHTML = `<div class="alert alert-danger">Error: Could not load data from data.json. Please ensure the file exists and you are running this from a web server.</div>`;
        });
    function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}
    function initializePage() {
        document.querySelectorAll('input[name="benchmarkRadio"]').forEach(r => r.addEventListener('change', e => { currentBenchmark = e.target.value; updateSubMetricButtons(); updateChart(); }));
        document.querySelectorAll('input[name="viewRadio"]').forEach(r => r.addEventListener('change', e => { currentView = e.target.value; updateChart(); }));
        document.getElementById('toggleUnknownSize').addEventListener('change', updateChart);
        window.addEventListener('resize', () => myChart.resize());

        document.querySelectorAll('.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const sortKey = th.dataset.sort;

                if (sortState.key === sortKey) {
                    sortState.order = sortState.order === 'desc' ? 'asc' : 'desc';
                } else {
                    sortState.key = sortKey;
                    sortState.order = 'desc';
                }

                document.querySelectorAll('.sortable').forEach(otherTh => {
                    if (otherTh === th) {
                        otherTh.textContent = `${otherTh.textContent.replace(/ [↓↑]/, '')} ${sortState.order === 'desc' ? '↓' : '↑'}`;
                    } else {
                        otherTh.textContent = otherTh.textContent.replace(/ [↓↑]/, '');
                    }
                });
                updateChart();
            });
        });
    
        updateSubMetricButtons();
        updateChart();
    }
function updateSubMetricButtons() {
    const metrics = subMetricsMap[currentBenchmark];
    subMetricGroup.innerHTML = '';

    if (metrics.length === 0) {
        currentSubMetric = 'vcode_overall';
        subMetricGroup.style.height = '';
        return;
    }
    
    subMetricGroup.style.height = 'auto';
    if (!metrics.includes(currentSubMetric)) currentSubMetric = 'avg';

    if (metrics.length > 7) { 
        let optionsHTML = metrics.map(metric => 
            `<option value="${metric}" ${metric === currentSubMetric ? 'selected' : ''}>${metric.toUpperCase()}</option>`
        ).join('');
        
        subMetricGroup.className = '';
        subMetricGroup.innerHTML = `
            <select class="form-select form-select-sm" id="subMetricSelect" style="width: auto; min-width: 200px;">
                ${optionsHTML}
            </select>
        `;
        document.getElementById('subMetricSelect').addEventListener('change', e => {
            currentSubMetric = e.target.value;
            updateChart();
        });

    } else { 
        subMetricGroup.className = 'btn-group btn-group-sm';
        let buttonsHTML = metrics.map(metric => `
            <input type="radio" class="btn-check" name="subMetricRadio" id="${metric}" value="${metric}" ${metric === currentSubMetric ? 'checked' : ''} />
            <label class="btn btn-outline-secondary" for="${metric}">${metric.toUpperCase()}</label>
        `).join('');

        subMetricGroup.innerHTML = buttonsHTML;
        
        document.querySelectorAll('input[name="subMetricRadio"]').forEach(r => r.addEventListener('change', e => {
            currentSubMetric = e.target.value;
            updateChart();
        }));
    }
}
    function getFilteredData() {
        let data = JSON.parse(JSON.stringify(chartData));
        if (!document.getElementById('toggleUnknownSize').checked) { data = data.filter(m => m.size !== null); }
        return data.map(m => {
            let score = (currentBenchmark === 'vcode_overall') ? m.scores.vcode_overall : m.scores[currentBenchmark]?.[currentSubMetric];
            return { ...m, score };
        }).filter(m => m.score != null).sort((a, b) => b.score - a.score);
    }
    function updateChart() {
        myChart.showLoading({ text: 'Loading...', color: '#0d6efd', maskColor: 'rgba(255, 255, 255, 0.8)' });
        setTimeout(() => {
            const data = getFilteredData();
            let chartOption;
            switch (currentView) {
                case 'recommendation': chartOption = getRecommendationOption(data); break;
                case 'size': chartOption = getSizeOption(data); break;
                case 'time': chartOption = getTimeOption(data); break;
            }
            renderTable();
            myChart.hideLoading();
            myChart.setOption(chartOption, true);
        }, 100);
    }
    function getScoreColor(score) {
        if (score >= 85) return "#198754"; if (score >= 75) return "#0dcaf0"; if (score >= 65) return "#ffc107"; return "#dc3545";
    }

    function getSequentialColor(score) {
        const earthScale = [
            '#ffc9c9',
            '#ffa8a8',
            '#ff9f9f',
            '#f89d9d',
            '#ff8787',
            '#fb7575',
            '#fb6363',
            '#fa5252',
            '#fa5252',
            '#fa5252' 
        ];
        if (score === null || score < 0) return '#f8f9fa'; 
        const index = Math.floor(score / 10);
        return earthScale[Math.min(index, 9)];
    }
    function getRecommendationOption(data) {
        const chartData = data.slice(0, 15);
        const barData = chartData.map(model => ({ value: model.score, name: model.modelName, displayName: `${model.modelName}`, itemStyle: { color: getSequentialColor(model.score), decal: model.isThinkingModel ? { symbol: 'rect', dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: 0.785, color: 'rgba(0,0,0,0.4)' } : null }, ...model }));
        return {
            title: { text: 'Top Models', left: 'center', textStyle: { fontWeight: 'bold', fontSize: 15 } },
            tooltip: { trigger: 'item', ...baseTooltipStyle, formatter: p => `<b>${p.data.modelName}</b><br/>Score: ${p.data.score.toFixed(1)}<br/>Size: ${p.data.size != null ? p.data.size + 'B' : 'Unknown'}<br/>Date: ${p.data.date}` },
            legend: { data: ['Standard', 'Thinking'], top: 30, selectedMode: false },
            grid: { containLabel: true, left: 80, right: 30, bottom: 80, top: 60 },
            xAxis: { type: 'category', data: barData.map(d => d.displayName), axisLabel: { interval: 0, rotate: 30, align: 'right', fontSize: 10 } },
            yAxis: { type: 'value', name: 'Score', nameTextStyle: { fontSize: 12 }, axisLabel: { fontSize: 10 }, splitLine: { lineStyle: { color: '#e9e9e9', type: 'dashed' } } },
            series: [
                { name: 'Models', type: 'bar', barWidth: '60%', data: barData, label: { show: true, position: 'top', fontWeight: 'bold', fontSize: 11, formatter: p => p.value.toFixed(1) }},
                { name: 'Standard', type: 'bar', data: [], itemStyle: { color: '#ff8787'} },
                { name: 'Thinking', type: 'bar', data: [], itemStyle: { color: '#ff8787', decal: { symbol: 'rect', dashArrayX: [1, 0], dashArrayY: [2, 5], rotation: 0.785, color: 'rgba(0,0,0,0.4)'} } }
            ]
        };
    }
    function getSizeOption(data) {
        const maxScore = Math.max(0, ...data.map(m => m.score));

        return {
            title: { text: 'Performance vs. Model Size', left: 'center', textStyle: { fontWeight: 'bold', fontSize: 15 } },
            tooltip: {
                trigger: 'item', ...baseTooltipStyle,
                axisPointer: { type: 'cross', lineStyle: { color: '#888', width: 1, type: 'dashed' } },
                formatter: params => {
                    const model = chartData.find(m => m.modelName === params.name);
                    if (!model) return '';
                    if (params.componentType === 'markLine') {
                        return `<b>${model.modelName}</b><br/>Score: ${params.value.toFixed(1)}<br/>Size: Unknown<br/>Date: ${model.date}`;
                    }
                    return `<b>${model.modelName}</b><br/>Score: ${params.value[1].toFixed(1)}<br/>Size: ${params.value[0]}B<br/>Date: ${model.date}`;
                }
            },
            grid: { containLabel: true, left: 15, right: 150, bottom: 30, top: 60 },
            xAxis: { type: 'value', name: 'Size (B)', nameLocation: 'middle', nameGap: 25, nameTextStyle: { fontSize: 12 }, axisLabel: { fontSize: 10 } , splitLine: { show: false } },
            yAxis: { 
                type: 'value', 
                name: 'Score', 
                axisLine: { show: false }, 
                nameTextStyle: { fontSize: 12 }, 
                axisLabel: { fontSize: 10 }, 
                splitLine: { lineStyle: { color: '#e9e9e9', type: 'dashed' } },
                max: Math.ceil(maxScore * 1.07)
            },
            series: [{ 
                type: 'scatter', 
                data: data.filter(m => m.size !== null).map(m => ({ name: m.modelName, value: [m.size, m.score] })), 
                label: { show: true, position: 'top', fontSize: 10, color: '#666', formatter: '{b}' },
                symbolSize: 12, 
                itemStyle: { borderColor: 'rgba(0,0,0,0.2)', borderWidth: 1 }, 
                markLine: { 
                    symbol: 'none',
                    tooltip: { trigger: 'item' },
                    data: data.filter(m => m.size === null).map(m => ({ 
                        name: m.modelName, yAxis: m.score, 
                        label: { show: true, position: 'end', formatter: `{b}`, fontSize: 10, color: '#6c757d', distance: 8 },
                        lineStyle: { color: '#adb5bd' }
                    })) 
                } 
            }]
        };
    }
    function getTimeOption(data) {
        const knownSizeData = data.filter(m => m.date && m.size !== null);
        const unknownSizeData = data.filter(m => m.date && m.size === null);
        const unifiedLabelStyle = {
            show: true,
            position: 'top',
            fontSize: 10,
            color: '#666',
            formatter: '{b}'
        };

        let axisMin = null;
        let axisMax = null;

        const allDatedData = chartData.filter(m => m.date);
        if (allDatedData.length > 0) {
            const allTimestamps = allDatedData.map(item => new Date(item.date).getTime());
            const minTimestamp = Math.min(...allTimestamps);
            const maxTimestamp = Math.max(...allTimestamps);
            const span = maxTimestamp - minTimestamp;
            const padding = (span > 0) ? span * 0.05 : 1000 * 60 * 60 * 24 * 30 * 3;
            axisMin = new Date(minTimestamp - padding);
            axisMax = new Date(maxTimestamp + padding);
        }
        return {
            title: { text: 'Performance Over Time', left: 'center', textStyle: { fontWeight: 'bold', fontSize: 15 } },
            tooltip: {
                trigger: 'item', ...baseTooltipStyle,
                axisPointer: { type: 'cross', lineStyle: { color: '#888', width: 1, type: 'dashed' } },
                formatter: p => {
                    const model = chartData.find(m => m.modelName === p.name);
                    return `<b>${p.name}</b><br/>Score: ${p.value[1].toFixed(1)}<br/>Date: ${new Date(p.value[0]).toLocaleDateString('en-CA')}<br/>Size: ${model.size !=null ? model.size + 'B' : 'Unknown'}`;
                }
            },
            grid: { containLabel: true, left: 15, right: 30, bottom: 30, top: 60 },
            xAxis: { type: 'time', name: 'Date', nameLocation: 'middle', nameGap: 25, nameTextStyle: { fontSize: 12 }, axisLabel: { fontSize: 10 }, min: axisMin, max: axisMax},
            yAxis: { type: 'value', name: 'Score', axisLine: { show: false }, nameTextStyle: { fontSize: 12 }, axisLabel: { fontSize: 10 }, splitLine: { lineStyle: { color: '#e9e9e9', type: 'dashed' } } },
            visualMap: { 
                show: false, min: 0, max: 200, dimension: 2, 
                inRange: { symbolSize: [8, 100] },
                seriesIndex: 0
            },
            series: [
                { 
                    name: 'Known Size Models',
                    type: 'scatter', 
                    data: knownSizeData.map(m => ({ name: m.modelName, value: [m.date, m.score, m.size] })), 
                    itemStyle: { color: COLORS.general, borderColor: 'rgba(255,255,255,0.4)', borderWidth: 1 }, 
                    label: unifiedLabelStyle
                },
                {
                    name: 'Unknown Size Models',
                    type: 'scatter',
                    symbolSize: 50,
                    itemStyle: { color: COLORS.unknown, borderColor: 'rgba(255,255,255,0.4)', borderWidth: 1 },
                    data: unknownSizeData.map(m => ({ name: m.modelName, value: [m.date, m.score, 1] })),
                    label: unifiedLabelStyle
                }
            ]
        };
    }

function renderTable() {
    const tbody = document.getElementById('leaderboard-tbody');
    tbody.innerHTML = '';
    const TOTAL_SAMPLES = {
        general: 200,
        professional: 146,
        vision_centric: 100
    };
    const TOTAL_OVERALL_SAMPLES = TOTAL_SAMPLES.general + TOTAL_SAMPLES.professional + TOTAL_SAMPLES.vision_centric;
    const dataWithSuccessRate = chartData.map(model => {
        const gen_samples = model.scores.general?.samples ?? 0;
        const prof_samples = model.scores.professional?.samples ?? 0;
        const vis_samples = model.scores.vision_centric?.samples ?? 0;

        const gen_rate = (TOTAL_SAMPLES.general > 0) ? (gen_samples / TOTAL_SAMPLES.general * 100) : 0;
        const prof_rate = (TOTAL_SAMPLES.professional > 0) ? (prof_samples / TOTAL_SAMPLES.professional * 100) : 0;
        const vis_rate = (TOTAL_SAMPLES.vision_centric > 0) ? (vis_samples / TOTAL_SAMPLES.vision_centric * 100) : 0;

        const total_generated_samples = gen_samples + prof_samples + vis_samples;
        const overall_rate = (TOTAL_OVERALL_SAMPLES > 0) ? (total_generated_samples / TOTAL_OVERALL_SAMPLES * 100) : 0;

        return {
            ...model,
            success_rate: overall_rate,
            success_details: {
                general: gen_rate,
                professional: prof_rate,
                vision_centric: vis_rate
            }
        };
    }).filter(model => !model.modelName.startsWith('Orig. Image'));

    const sortedData = [...dataWithSuccessRate].sort((a, b) => {
        let valA = a.scores[sortState.key] ?? a[sortState.key];
        let valB = b.scores[sortState.key] ?? b[sortState.key];
        
        valA = valA ?? (sortState.order === 'desc' ? -Infinity : Infinity);
        valB = valB ?? (sortState.order === 'desc' ? -Infinity : Infinity);
        
        if (typeof valA === 'object' && valA !== null) valA = valA.avg;
        if (typeof valB === 'object' && valB !== null) valB = valB.avg;
        
        return sortState.order === 'desc' ? valB - valA : valA - valB;
    });

    if (sortedData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center">No data to display.</td></tr>';
        return;
    }

    sortedData.forEach((model, index) => {
        const overallScore = model.scores.vcode_overall;
        const barWidth = overallScore ? Math.min(overallScore, 100) : 0;
        const barColor = getSequentialColor(overallScore);

        const tooltipContent = `
            General: ${model.success_details.general.toFixed(1)}%<br>
            Professional: ${model.success_details.professional.toFixed(1)}%<br>
            Vision-centric: ${model.success_details.vision_centric.toFixed(1)}%
        `.replace(/"/g, '&quot;');

        const row = `
            <tr>
                <th scope="row" class="text-center">${index + 1}</th>
                <td class="model-cell">
                    <div class="score-bar" style="width: ${barWidth}%; background-color: ${barColor};"></div>
                    <a href="#" class="model-link">
                        ${index < 3 ? ['🥇', '🥈', '🥉'][index] + ' ' : ''}
                        ${model.modelName}
                    </a>
                </td>
                <td class="text-end fw-bold">${overallScore?.toFixed(1) ?? 'N/A'}</td>      
                <td class="text-end">${model.scores.general?.avg?.toFixed(1) ?? 'N/A'}</td>
                <td class="text-end">${model.scores.professional?.avg?.toFixed(1) ?? 'N/A'}</td>
                <td class="text-end">${model.scores.vision_centric?.avg?.toFixed(1) ?? 'N/A'}</td>
                <td class="text-end">${model.sigLipScore?.toFixed(1) ?? 'N/A'}</td>
                <td class="text-end">${model.codeToken?.toFixed(1) ?? 'N/A'}</td>
                <td class="text-end">
                    <span 
                        data-bs-toggle="tooltip" 
                        data-bs-html="true" 
                        data-bs-placement="left"
                        title="${tooltipContent}">
                        ${model.success_rate.toFixed(1)}%
                    </span>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });

    initializeTooltips();
}

    document.querySelectorAll('input[name="benchmarkRadio"]').forEach(r => r.addEventListener('change', e => { currentBenchmark = e.target.value; updateSubMetricButtons(); updateChart(); }));
    document.querySelectorAll('input[name="viewRadio"]').forEach(r => r.addEventListener('change', e => { currentView = e.target.value; updateChart(); }));
    document.getElementById('toggleUnknownSize').addEventListener('change', updateChart);
    window.addEventListener('resize', () => myChart.resize());
    updateSubMetricButtons();
    updateChart();
})
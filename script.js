const videoInput = document.getElementById('videoUrl');
const downloadBtn = document.getElementById('downloadBtn');
const status = document.getElementById('status');
const nameInput = document.getElementById('filename');
const progressBar = document.getElementById('progress');
const progressText = document.getElementById('progressText');
const againBtn = document.getElementById('againBtn');

function setStatus(message, isError = false){
    status.textContent = message;
    status.style.color = isError ? '#c53030' : '';
}

function formatMb(bytes){
    return (bytes / (1024 * 1024)).toFixed(2);
}

function setProgress(percent, downloaded = 0, total = 0){
    const value = Math.min(100, Math.max(0, percent));
    progressBar.value = value;
    if(total > 0){
        progressText.textContent = `${formatMb(downloaded)} MB / ${formatMb(total)} MB (${value}%)`;
    }else{
        progressText.textContent = `${value}%`;
    }
}

// Enable / disable download button based on input
videoInput.addEventListener('input', () => {
    downloadBtn.disabled = !videoInput.value.trim();
});

async function downloadVideo(){
    const videoUrl = videoInput.value.trim();
    const fileName = nameInput ? nameInput.value.trim() : '';
    if(!videoUrl) return setStatus('Please enter a valid Pinterest video URL.', true);

    setStatus('Preparing download...');
    downloadBtn.disabled = true;
    downloadBtn.classList.add('loading');
    againBtn.hidden = true;
    setProgress(0);

    try{
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: videoUrl, name: fileName })
        });

        const data = await response.json();
        if(!response.ok || !data.ok){
            throw new Error(data.error || 'Download failed.');
        }
        await pollProgress(data.job_id);
    }catch(err){
        setStatus(err.message, true);
    }finally{
        downloadBtn.disabled = false;
        downloadBtn.classList.remove('loading');
    }
}

async function pollProgress(jobId){
    if(!jobId){
        setStatus('Missing job id from server.', true);
        return;
    }

    let done = false;
    while(!done){
        const res = await fetch(`/api/status/${jobId}`);
        const data = await res.json();

        if(data.total > 0){
            const percent = Math.round((data.downloaded / data.total) * 100);
            setProgress(percent, data.downloaded, data.total);
        }

        if(data.status === 'done'){
            setProgress(100, data.total, data.total);
            setStatus(`Download complete: ${data.file}`);
            againBtn.hidden = false;
            done = true;
        }else if(data.status === 'error'){
            setStatus(data.error || 'Download failed.', true);
            done = true;
        }else{
            setStatus('Downloading...');
            await new Promise(r => setTimeout(r, 500));
        }
    }
}

againBtn.addEventListener('click', () => {
    videoInput.value = '';
    nameInput.value = '';
    setProgress(0);
    setStatus('Paste a new URL to start another download.');
    downloadBtn.disabled = true;
    againBtn.hidden = true;
});

downloadBtn.addEventListener('click', downloadVideo);
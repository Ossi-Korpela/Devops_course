
const express = require('express');
const { execSync } = require('child_process');



const app = express();

function systemInfo() {
    const ip = execSync('hostname -I').toString().trim();
    const processes = execSync('ps -ax').toString();
    const disk = execSync('df -h /').toString();
    const uptime = execSync('uptime -p').toString().trim();
    return {
        "IP address": ip,
        "Processes": processes,
        "Disk space": disk,
        "Uptime": uptime
    };
}

app.get('/', (req, res) => {
    const info = systemInfo();
    res.json(info);
});

app.listen(8200, () => {
    console.log('Service2 listening on port 8200');
});

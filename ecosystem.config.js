module.exports = {
  apps: [{
    name: 'association-mining',
    script: 'app.py',
    interpreter: 'python3',
    cwd: '/home/duy/KHDL_demo_main',
    env: {
      PYTHONPATH: '/home/duy/KHDL_demo_main'
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};

# SIM-ID-I XPCS Bluesky Instrument

## Installation Steps

First, download the package from github:

```bash
git clone git@github.com:MDecarabas/test_bs_id.git
cd test_bs_id
```

Then create the conda environment with mamba:

```bash
export env_name='bs_test'
conda create -n $env_name python=3.10
conda activate $env_name
pip install -e ".[dev]"
```


## Running Bluesky Session
### With Ipython

```bash
cd scripts
./bs_ipy_starter.sh
```

Then Inside the ipython shell
```
RE(demo_sim_1d())
```

### With Queserver

Inside one terminal
```bash
cd scripts
./run_qs.sh
```
Inside another terminal
```bash
qserver environment open
qserver queue add plan '{"name": "demo_sim_1d"}'
qserver queue start
```

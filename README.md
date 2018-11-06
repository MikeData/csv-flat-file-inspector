
# CSV Inspector

Structurally agnostic tool for inspecting/validating one-observation-per-row dimensioned CSV data.


## Install

`pip install git+https://github.com/ONS-OpenData/csvInspect.git`


## Usage

```
from csvInspect.framework import inspector
inspector(<CSV>, <url for config>)
```

example:
```
warnings = inspector("sample.csv", "https://raw.githubusercontent.com/mikeAdamss/validation-configs/master/example/config.json")
print(warnings)
```

The config is just a set of instructions per-dataset. There's an example one here:
`https://github.com/mikeAdamss/validation-configs/blob/master/example/config.json`

`warnings` as shown above is just a dictionary.

NOTE - most issues will throw an error. Warnings will currently only be present when sparsity is present but not
at a level you have defined as unnaccepable.




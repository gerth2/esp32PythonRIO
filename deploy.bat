:: copy all source files
for %%f in (*.py) do (
    mpremote fs cp %%f :%%f
)

mpremote soft-reset

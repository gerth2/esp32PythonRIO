mpremote mkdir :private
mpremote mkdir :www

:: copy all source files
for %%f in (*.py) do (
    mpremote fs cp %%f :%%f
)

for %%f in (private/*.py) do (
    mpremote fs cp private/%%f :private/%%f
)

for %%f in (www/*.*) do (
    mpremote fs cp www/%%f :www/%%f
)

mpremote soft-reset

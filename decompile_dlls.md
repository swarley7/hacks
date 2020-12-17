Process for decompiling a number of DLL files to (probably not) compilable source projects:
# Install dotnet (https://dotnet.microsoft.com/download)
# Install ilspycmd (dotnet tool install ilspycmd -g)
# Create the following script and chmod +x
# Run the script from the directory containing any DLL files

```bash
#!/bin/bash
for i in `ls *.dll`; do mkdir "./${i}-decomp"; $HOME/.dotnet/tools/ilspycmd -p -o "./${i}-decomp" $i ; done
```

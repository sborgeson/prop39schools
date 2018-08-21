install.packages(c("devtools"))

# build_vignettes=T will build vignettes that serve as examples of usage
# however, this will invoke other dependencies that might complicate things.
# It can be set to F to just get the core code installed, but much of the documentation
# effort to date has been in the form of vignettes.
devtools::install_github("convergenceda/visdom", build_vignettes=T )

##Confirming that the package and documentation is in place Now check that you can load VISDOM and use it.

library(visdom)

# Browse through the available vignettes.
# if you built them above, you can browse well formatted 
# code vignettes that provide example usage (run commented line for a menu of options.
# browseVignettes('visdom')

#Or the original/old school way.
# to list
vignette(package='visdom')
# to display a specific one as help
vignette('example_feature_extraction',package='visdom')

??visdom

# Now install load shape code if you want to cluster load shapes like
# https://ieeexplore.ieee.org/document/6693793/
devtools::install_github("convergenceda/visdomloadshape", build_vignettes=T )


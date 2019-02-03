#!/bin/bash
mkdir consolidated
cd consolidated
rsync -r --copy
-links ../../Python/* ./ 

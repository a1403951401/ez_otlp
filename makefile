

### help: Print this help
help: #check build clean upload
	@awk ' \
		match($$0,/^###(@(\w+))? [Hh]elp: /,m) \
		{c=m[2];h=substr($$0,RLENGTH);next} \
		h&&/^[[:alpha:]][[:alnum:]_/-]+:/ \
		{help[c][idx[c]++]=sprintf("\033[36m%s\033[0m\t%s", substr($$1,1,index($$1,":")-1),h)} \
		1{c=0;h=0} \
		END{ \
			n=asorti(help, help_); \
			for (c = 1; c <= n; c++) { \
				if(help_[c]){indent="  ";printf "\n%s:\n", help_[c]}\
				asort(help[help_[c]]); \
				for(x in help[help_[c]]){print indent help[help_[c]][x]} \
			} \
		}' $(MAKEFILE_LIST) | column -s$$'\t' -tL


###@build Help: upload to pypi
build:
	uv build && \
	 twine upload dist/* && \
	 rm -rf build dist *.egg-info

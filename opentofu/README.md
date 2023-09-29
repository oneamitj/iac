# Execution
First you need OpenTofu. As writing of this there is NO binary for OpenTofu. So what you do? Ofcourse build the binary.
1. Build `tofu` binary from OpenTofu source


      # Go v1.19+
      brew install go
      git clone git@github.com:opentofu/opentofu.git
      go install ./cmd/tofu
      go build ./cmd/tofu
      sudo ln -s `pwd`/tofu /usr/local/bin/tofu

2. Add AWS credentials


      export AWS_ACCESS_KEY_ID="-------"
      export AWS_SECRET_ACCESS_KEY="-----"

3. Run terraform


      tofu init
      tofu plan
      tofu apply
      tofu destroy


Hurray! All (almost) the code from Terraform works as-it-is. Even the working folder and file are named terraform.
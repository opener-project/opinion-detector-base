require 'bundler/gem_tasks'
require_relative 'ext/hack/support'

desc 'Lists all the files of the Gemspec'
task :files do
  gemspec = Gem::Specification.load('opener-opinion-detector-base.gemspec')

  puts gemspec.files.sort
end

desc 'Verifies the requirements'
task :requirements do
  verify_requirements
end

desc 'Installs Python packages in core/site-packages'
task :compile => :requirements do
  requirements = {
    PRE_BUILD_REQUIREMENTS   => 'pre_build',
    PRE_INSTALL_REQUIREMENTS => 'pre_install'
  }

  requirements.each do |file, directory|
    install_python_packages(file, directory)
  end
end

namespace :clean do
  desc 'Removes Python .pyc files'
  task :pyc do
    sh('find . -name "*.pyc" -delete')
    sh('find . -name "*.pyo" -delete')
  end

  desc 'Removes tmp files'
  task :tmp do
    sh("rm -f #{File.join(TMP_DIRECTORY, '*.kaf')}")
  end

  desc 'Removes packages from core/site-packages'
  task :packages do
    each_file(PYTHON_SITE_PACKAGES) do |group|
      each_file(group) do |directory|
        sh("rm -rf #{directory}")
      end
    end
  end

  desc 'Removes all built Gem files'
  task :gems do
    sh('rm -f pkg/*.gem')
  end
end

desc 'Cleans up the repository'
task :clean => ['clean:pyc', 'clean:tmp', 'clean:packages', 'clean:gems']

desc 'Runs the tests'
task :test => :compile do
  sh('cucumber features')
end

desc 'Performs preparations for building the Gem'
task :before_build => [:requirements, 'clean:pyc'] do
  install_python_packages(PRE_BUILD_REQUIREMENTS, 'pre_build')
end

task :build   => :before_build
task :default => :test

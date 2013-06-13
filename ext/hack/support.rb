require 'opener/build-tools'

# Directory where packages will be installed to.
PYTHON_SITE_PACKAGES = File.expand_path(
  '../../../core/site-packages',
  __FILE__
)

# Directory containing the temporary files.
TMP_DIRECTORY = File.expand_path('../../../tmp', __FILE__)

# Path to the pip requirements file used to install requirements before
# packaging the Gem.
PRE_BUILD_REQUIREMENTS = File.expand_path(
  '../../../pre_build_requirements.txt',
  __FILE__
)

# Path to the pip requirements file used to install requirements upon Gem
# installation.
PRE_INSTALL_REQUIREMENTS = File.expand_path(
  '../../../pre_install_requirements.txt',
  __FILE__
)

##
# Installs the packages in the requirements file in a specific directory.
#
# @param [String] file The requirements file to use.
# @param [String] target The target directory to install packages in.
#
def pip_install(file, target)
  sh("pip install --requirement=#{file} --target=#{target}")
end

##
# Calls the supplied block for each file in the given directory, ignoring '.'
# and '..'.
#
# @param [String] directory
# @yield [String]
#
def each_file(directory)
  directory_contents(directory).each do |path|
    yield path
  end
end

##
# Verifies the requirements to install thi Gem.
#
def verify_requirements
  require_executable('python')
  require_version('python', python_version, '2.7.0')
  require_executable('pip')
end

##
# Returns an Array containing the contents of a given directory, excluding '.'
# and '..'.
#
# @param [String] directory
#
def directory_contents(directory)
  return Dir.glob(File.join(directory, '*'))
end

##
# Installs a set of Python packages in a given directory based on a
# requirements file. If the directory is not empty this process is aborted.
#
# @param [String] file The requirements file to install.
# @param [String] directory The name of the directory in core/site-packages to
#  install the packages in to.
#
def install_python_packages(requirements, directory)
  path = File.join(PYTHON_SITE_PACKAGES, directory)

  return unless directory_contents(path).empty?

  pip_install(requirements, path)
end

include Opener::BuildTools

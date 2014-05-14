require_relative '../../lib/opener/opinion_detectors/base'
require 'rspec/expectations'
require 'tempfile'

def kernel_root
  File.expand_path("../../../", __FILE__)
end

def kernel(language)
  return Opener::OpinionDetectors::Base.new(
    :language => language,
    :args => ['-no-time']
  )
end

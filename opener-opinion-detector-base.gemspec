require File.expand_path('../lib/opener/opinion_detectors/base/version', __FILE__)

generated = Dir.glob('core/site-packages/pre_build/**/*')

Gem::Specification.new do |gem|
  gem.name        = 'opener-opinion-detector-base'
  gem.version     = Opener::OpinionDetectors::Base::VERSION
  gem.authors     = ['development@olery.com']
  gem.summary     = 'Base Opinion Detector for english and dutch.'
  gem.description = gem.summary
  gem.homepage    = 'http://opener-project.github.com/'

  gem.required_ruby_version = '>= 1.9.2'

  gem.files       = (`git ls-files`.split("\n") + generated).sort
  gem.executables = gem.files.grep(%r{^bin/}).map{ |f| File.basename(f) }
  gem.test_files  = gem.files.grep(%r{^(test|spec|features)/})
  gem.extensions  = ['ext/hack/Rakefile']

  gem.add_dependency 'opener-build-tools'
  gem.add_dependency 'rake'

  gem.add_development_dependency 'rspec'
  gem.add_development_dependency 'cucumber'
end

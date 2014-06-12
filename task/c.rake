namespace :c do
  desc 'Compiles the vendored C code'
  task :compile do
    source = File.expand_path('../../core/vendor/src', __FILE__)
    build  = File.expand_path('../../core/vendor/build', __FILE__)

    Dir.chdir(File.join(source, 'liblbfgs')) do
      sh "./configure --prefix=#{build}"
      sh 'make && make install && make distclean'
    end

    Dir.chdir(File.join(source, 'crfsuite')) do
      sh "./configure --prefix=#{build} --with-liblbfgs=#{build}"
      sh 'make && make install && make distclean'
    end

    Dir.chdir(File.join(source, 'svm_light')) do
      sh 'make'
      sh "mv svm_classify svm_learn #{File.join(build, 'bin')}"
      sh 'make clean'
    end
  end
end

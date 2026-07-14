#git-archive-all --prefix OrcaSlicer-2.3.2/ --force-submodules  ~/rpmbuild/SOURCES/OrcaSlicer-2.3.2.tar.gz

#git-archive-all --prefix OrcaSlicer-2.4.2/ --force-submodules  ~/rpmbuild/SOURCES/OrcaSlicer-2.4.2.tar.gz

#rpmbuild -bs OrcaSlicer.spec

mock -r fedora-44-x86_64 --define "_smp_mflags -j4" --enable-network --rebuild /home/fuzi/rpmbuild/SRPMS/OrcaSlicer-2.4.2-1.fc44.src.rpm

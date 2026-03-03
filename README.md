| Package&nbsp;name | Supported&nbsp;targets |
| :--- | :--- |
| kompot<br/>kompot-setup | el9 |
<br/>

## Build:

The package can be built easily using the rpmbuild-docker script provided in this repository. In order to use this script, _**a functional Docker environment is needed**_, with ability to pull Rocky Linux (el9) images from internet if not already downloaded.

```
$ ./rpmbuild-docker -d el9
```

## Prebuilt packages:

Builds of these packages are available on ZENETYS yum repositories:<br/>
https://packages.zenetys.com/projects/kompot/latest/redhat/

## Documentation:

Some pieces of documentation are available in [zenetys/kompot-core/doc](https://github.com/zenetys/kompot-core/tree/master/doc).</br>
See page [zenetys/kompot-core/doc/install_rpm.md](https://github.com/zenetys/kompot-core/tree/master/doc/install_rpm.md) for KOMPOT installation from RPM package.

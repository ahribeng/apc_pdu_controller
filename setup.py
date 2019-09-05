from distutils.core import setup
setup(
  name = 'apc_pdu_controller',
  packages = ['apc_pdu_controller'],
  version = '0.1',
  license='MIT',
  description = 'SSH Control for APC Model PDU's',
  author = 'Ahriben Gonzalez',
  author_email = 'ahribeng@gmail.com',
  url = 'https://github.com/user/ahribeng',
  download_url = 'https://github.com/ahribeng/apc_pdu_controller/archive/v_01.tar.gz',
  keywords = ['SSH', 'APC', 'PDU'],
  install_requires=[
          'paramiko'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
      ],
)

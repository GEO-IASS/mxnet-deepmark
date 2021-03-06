from __future__ import absolute_import

import mxnet as mx
import numpy as np

try:
    from utils.memonger import search_plan
except:
    import sys
    sys.path.append("../utils/")
    from memonger import search_plan

def conv_factory(data, num_filter, kernel, stride=(1, 1), pad=(1, 1), with_bn=False):
    net = mx.sym.Convolution(data,
                             num_filter=num_filter,
                             kernel=kernel,
                             stride=stride,
                             pad=pad)
    if with_bn:
        net = mx.sym.BatchNorm(net, fix_gamma=False)
    net = mx.sym.Activation(net, act_type="relu")
    net._set_attr(mirror_stage='True')
    return net

def get_symbol():
    net = mx.sym.Variable("data")
    # group 0
    net = conv_factory(net, num_filter=64, kernel=(11, 11), stride=(4, 4), pad=(2, 2))
    net = mx.sym.Pooling(net, kernel=(3, 3), stride=(2, 2), pool_type="max")
    # group 1
    net = conv_factory(net, num_filter=192, kernel=(5, 5), stride=(1, 1), pad=(2, 2))
    net = mx.sym.Pooling(net, kernel=(3, 3), stride=(2, 2), pool_type="max")
    # group 2
    net = conv_factory(net, num_filter=384, kernel=(3, 3), stride=(1, 1), pad=(1, 1))
    net = conv_factory(net, num_filter=256, kernel=(3, 3), stride=(1, 1), pad=(1, 1))
    net = conv_factory(net, num_filter=256, kernel=(3, 3), stride=(1, 1), pad=(1, 1))
    net = mx.sym.Pooling(net, kernel=(3, 3), stride=(2, 2), pool_type="max")
    # group 3
    net = mx.sym.Flatten(net)
    net = mx.sym.Dropout(net, p=0.5)
    net = mx.sym.FullyConnected(net, num_hidden=4096)
    net = mx.sym.Activation(net, act_type="relu")
    net._set_attr(mirror_stage='True')
    # group 4
    net = mx.sym.Dropout(net, p=0.5)
    net = mx.sym.FullyConnected(net, num_hidden=4096)
    net = mx.sym.Activation(net, act_type="relu")
    net._set_attr(mirror_stage='True')
    # group 5
    net = mx.sym.FullyConnected(net, num_hidden=1000)
    # TODO(xxx): Test speed difference between SoftmaxActivation and SoftmaxOutput
    net = mx.sym.SoftmaxOutput(net, name="softmax")
    return net, [('data', (128, 3, 224, 224))], [('softmax_label', (128,))]

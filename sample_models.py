# Importing the libraries
import keras
from keras import backend as K
from keras.models import Model
from keras.layers import (BatchNormalization, Conv1D, Dense, Input, 
    TimeDistributed, Activation, Bidirectional, SimpleRNN, GRU, LSTM, Dropout, MaxPooling1D)

# Model 0
def simple_rnn_model(input_dim, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    simp_rnn = GRU(output_dim, return_sequences=True, implementation=2, name='rnn')(input_data)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(simp_rnn)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

# Model 1
def rnn_model(input_dim, units, activation, output_dim=29):
    """ Build a recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layer
    gru_layer = GRU(units, activation=activation,
                    return_sequences=True, implementation=2, name='rnn')(input_data)
    # Add batch normalization 
    bn_gru_layer = BatchNormalization(name = 'bn_gru_layer')(gru_layer)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_gru_layer)
    # Add softmax activation layer
    y_pred = Activation('softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

# Model 2
def cnn_rnn_model(input_dim, filters, kernel_size, conv_stride,
    conv_border_mode, units, output_dim=29):
    """ Build a recurrent + convolutional network for speech 
    """
    # Main acoustic input
    input_data = Input(name = 'the_input', shape = (None, input_dim))
    # Add convolutional layer
    conv_1d = Conv1D(filters, kernel_size, 
                     strides = conv_stride, 
                     padding = conv_border_mode,
                     activation = 'relu',
                     name = 'conv1d')(input_data)
    # Add batch normalization
    bn_cnn = BatchNormalization(name='bn_conv_1d')(conv_1d)
    # Add a recurrent layer
    lstm_layer = LSTM(units, 
                      activation='relu',
                      return_sequences=True, 
                      implementation=2, 
                      name='lstm_layer')(bn_cnn)
    # Add batch normalization
    bn_lstm_layer = BatchNormalization(name = 'bn_lstm_layer')(lstm_layer)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_lstm_layer)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: cnn_output_length(x, 
                                                      kernel_size, 
                                                      conv_border_mode, 
                                                      conv_stride)
    print(model.summary())
    return model

# Model 3
def cnn_output_length(input_length, filter_size, border_mode, stride,
                       dilation=1):
    """ Compute the length of the output sequence after 1D convolution along
        time. Note that this function is in line with the function used in
        Convolution1D class from Keras.
    Params:
        input_length (int): Length of the input sequence.
        filter_size (int): Width of the convolution kernel.
        border_mode (str): Only support `same` or `valid`.
        stride (int): Stride size used in 1D convolution.
        dilation (int)
    """
    if input_length is None:
        return None
    assert border_mode in {'same', 'valid'}
    dilated_filter_size = filter_size + (filter_size - 1) * (dilation - 1)
    if border_mode == 'same':
        output_length = input_length
    elif border_mode == 'valid':
        output_length = input_length - dilated_filter_size + 1
    return (output_length + stride - 1) // stride

# Model 4
def deep_rnn_model(input_dim, units, recur_layers, output_dim=29):
    """ Build a deep recurrent network for speech 
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # Add recurrent layers, each with batch normalization
    lstm_layer = LSTM(units, activation='relu', return_sequences=True, implementation=2, name='lstm_1')(input_data)
    bn_lstm = BatchNormalization(name = 'bn_lstm_1')(lstm_layer)
    
    lstm_layer_2 = LSTM(units, activation='relu', return_sequences=True, implementation=2, name='lstm_2')(bn_lstm)
    bn_lstm_2 = BatchNormalization(name = 'bn_lstm_2')(lstm_layer_2)
    
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bn_lstm_2)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

# Model 5
def bidirectional_rnn_model(input_dim, units, output_dim=29):
    """ Build a bidirectional recurrent network for speech
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    # TODO: Add bidirectional recurrent layer
    bidir_rnn = Bidirectional(LSTM(units, activation='relu',return_sequences=True, implementation=2, name='bidir_rnn'))(input_data)
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(bidir_rnn)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model

# Final model
def final_model(input_dim, units, output_dim=29):
    """ Build a bidirectional recurrent network for speech
    """
    # Main acoustic input
    input_data = Input(name='the_input', shape=(None, input_dim))
    
    # =============== 1st Layer =============== #
    # Add bidirectional recurrent layer
    bidirectional_rnn = Bidirectional(GRU(units, activation=None,return_sequences=True, implementation=2, name='bidir_rnn'))(input_data)
    # Add batch normalization
    batch_normalization = BatchNormalization(name = "batch_normalization_bidirectional_rnn")(bidirectional_rnn)
    # Add activation function
    activation = Activation('relu')(batch_normalization)
    # Add dropout
    drop = Dropout(rate = 0.1)(activation)
    
    # =============== 2nd Layer =============== #
    # Add bidirectional recurrent layer
    bidirectional_rnn = Bidirectional(GRU(units, activation=None,return_sequences=True, implementation=2, name='bidir_rnn'))(drop)
    # Add batch normalization
    batch_normalization = BatchNormalization(name = "bn_bidir_rnn_2")(bidirectional_rnn)
    # Add activation function
    activation = Activation('relu')(batch_normalization)
    # Add dropout
    drop = Dropout(rate = 0.1)(activation)
    
    # =============== 3rd Layer =============== #
    # Add a TimeDistributed(Dense(output_dim)) layer
    time_dense = TimeDistributed(Dense(output_dim))(drop)
    # Add softmax activation layer
    y_pred = Activation('softmax', name='softmax')(time_dense)
    
    # Specify the model
    model = Model(inputs=input_data, outputs=y_pred)
    model.output_length = lambda x: x
    print(model.summary())
    return model
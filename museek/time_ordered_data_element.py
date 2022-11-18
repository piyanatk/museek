import numbers

import numpy as np


class TimeOrderedDataElement:
    """
    Class to access an 'element' of time ordered data, e.g. the visibility data, or temperature values.
    All elements are internally stored with shape `(n_dump, n_frequency, n_receiver)`. If one of these axes only
    contains copies, e.g. the temperature is the same for all frequencies, then the corresponding shape is `1`.
    The elements should be accessed using one of the properties and manipulated with the public methods.
    """

    def __init__(self, array: np.ndarray, parent: 'TimeOrderedData'):
        """
        :param array: a `numpy` array of shape `(n_dump | 1, n_frequency | 1, n_receiver | n_dish | 1)`
        :param parent: instance of `TimeOrderedData`, to access the scan dump informations
        :raise ValueError: if `array is not 3-dimensional
        """
        if len(array.shape) != 3:
            raise ValueError(f'Input `array` needs to be 3-dimensional, got shape {array.shape}')
        self._array = array
        self._parent = parent

    def __mul__(self, other):
        """
        Multiplication of two `TimeOrderedDataElement`s and of one `TimeOrderedDataElement` with a `np.ndarray`.
        :raise ValueError: if attempting to multiply two instances of `TimeOrderedDataElement`
                           with different `_parent`s
        """
        if isinstance(other, TimeOrderedDataElement):
            if self._parent != other._parent:
                raise ValueError(
                    'Multiplication is only possible if both instances share the same `_parent` instance.'
                )
            return TimeOrderedDataElement(array=self._array * other._array, parent=self._parent)
        if isinstance(other, np.ndarray | numbers.Number):
            return TimeOrderedDataElement(array=self._array * other, parent=self._parent)

    def __getitem__(self, index: int | list[int]) -> np.ndarray:
        """ Returns `numpy`s getitem coupled with a squeeze. """
        return np.squeeze(self._array[index])

    @property
    def scan(self) -> np.ndarray:
        """ Returns a `numpy` `array` containing the 'scan' dumps of `self`. """
        return self.get_array(time=self._parent.scan_dumps)

    @property
    def track(self) -> np.ndarray:
        """ Returns a `numpy` `array` containing the 'track' dumps of `self`. """
        return self.get_array(time=self._parent.track_dumps)

    @property
    def slew(self) -> np.ndarray:
        """ Returns a `numpy` `array` containing the 'slew' dumps of `self`. """
        return self.get_array(time=self._parent.slew_dumps)

    @property
    def stop(self) -> np.ndarray:
        """ Returns a `numpy` `array` containing the 'stop' dumps of `self`. """
        return self.get_array(time=self._parent.stop_dumps)

    @property
    def full(self) -> np.ndarray:
        """ Returns a `numpy` `array` containing the all dumps of `self`. """
        return self.get_array()

    def mean(self, axis: int | list[int, int] | tuple[int, int]) -> 'TimeOrderedDataElement':
        """ Return the mean of `self` along `axis` as a `TimeOrderedDataElement`, i.e. the dimensions are kept. """
        return TimeOrderedDataElement(array=np.mean(self._array, axis=axis, keepdims=True), parent=self._parent)

    def get(self,
            *,  # force named parameters
            time: int | list[int] | slice | None = None,
            freq: int | list[int] | slice | None = None,
            recv: int | list[int] | slice | None = None,
            ) -> 'TimeOrderedDataElement':
        """
        Simplified indexing
        :param time: indices or slice along the zeroth (dump) axis
        :param freq: indices or slice along the first (frequency) axis
        :param recv: indices or slice along the second (receiver) axis
        :return: a copy of `self` indexed at the input indices
        """

        array = self._array.copy()

        if isinstance(time, int):
            time = [time]
        if isinstance(freq, int):
            freq = [freq]
        if isinstance(recv, int):
            recv = [recv]

        if time is not None:
            array = array[time, :, :]
        if freq is not None:
            array = array[:, freq, :]
        if recv is not None:
            array = array[:, :, recv]

        return TimeOrderedDataElement(array=array, parent=self._parent)

    def get_array(self, **kwargs) -> np.ndarray | float:
        """
        Returns `self` as a `numpy.ndarray` without extra dimensions.
        :param kwargs: passed on to `self.get()`
        """
        array = self.get(**kwargs)._array
        if array.shape == (1, 1, 1):  # squeeze behaves weirdly in this case
            return array[0, 0, 0]
        return np.squeeze(array)